"""Rate limiting middleware with Redis-backed sliding window.

Falls back to in-memory store if Redis is unavailable.
"""
import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("socforge.ratelimit")

# In-memory fallback
_mem_store: dict[str, list[float]] = defaultdict(list)
_redis_client = None
_redis_available = False


def _init_redis():
    """Try to connect to Redis for persistent rate limiting."""
    global _redis_client, _redis_available
    try:
        from app.config import settings
        import redis
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        _redis_client.ping()
        _redis_available = True
        logger.info("Rate limiter: Redis-backed (persistent)")
    except Exception:
        _redis_available = False
        logger.info("Rate limiter: in-memory fallback")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding window rate limiter — Redis-backed with in-memory fallback."""

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        _init_redis()

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for docs and health
        path = request.url.path
        if path.startswith(("/api/docs", "/api/openapi", "/api/redoc", "/api/health")):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        if _redis_available:
            allowed = self._check_redis(client_ip, now)
        else:
            allowed = self._check_memory(client_ip, now)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={"Retry-After": str(self.window_seconds)},
            )

        return await call_next(request)

    def _check_redis(self, client_ip: str, now: float) -> bool:
        """Redis-backed sliding window check."""
        try:
            key = f"rl:{client_ip}"
            window_start = now - self.window_seconds
            pipe = _redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, self.window_seconds)
            results = pipe.execute()
            current_count = results[1]
            return current_count < self.max_requests
        except Exception:
            # Redis failure → fall back to memory
            return self._check_memory(client_ip, now)

    def _check_memory(self, client_ip: str, now: float) -> bool:
        """In-memory sliding window check."""
        window_start = now - self.window_seconds
        _mem_store[client_ip] = [t for t in _mem_store[client_ip] if t > window_start]
        if len(_mem_store[client_ip]) >= self.max_requests:
            return False
        _mem_store[client_ip].append(now)
        return True
