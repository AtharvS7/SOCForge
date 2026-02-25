"""Audit logging middleware."""
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("socforge.audit")
logging.basicConfig(level=logging.INFO)


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round((time.time() - start) * 1000, 2)

        logger.info(
            f"[AUDIT] {request.method} {request.url.path} "
            f"status={response.status_code} "
            f"duration={duration}ms "
            f"client={request.client.host if request.client else 'unknown'}"
        )
        return response
