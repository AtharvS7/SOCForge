"""SOCForge - Enterprise SOC Threat Detection & Attack Simulation Platform."""
import logging
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.logging_config import setup_logging
from app.middleware.audit_logger import AuditLogMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.prometheus import PrometheusMiddleware, get_metrics_text
from app.routers import auth, alerts, events, detection, simulation, incidents, reports, dashboard
from app.routers import websocket as ws_router
from app.routers import users as users_router

logger = logging.getLogger("socforge")
_start_time = datetime.now(timezone.utc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    setup_logging()
    logger.info("SOCForge API starting up...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized.")
    yield
    logger.info("SOCForge API shutting down...")
    await engine.dispose()


app = FastAPI(
    title="SOCForge API",
    description="Enterprise SOC Threat Detection & Attack Simulation Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS — environment-conditional
_allowed_origins = (
    ["http://localhost:5173", "http://localhost:3000"]
    if settings.ENVIRONMENT == "production"
    else ["*"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting — 100 requests/minute per IP
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# Audit logging
app.add_middleware(AuditLogMiddleware)

# Prometheus metrics collection
app.add_middleware(PrometheusMiddleware)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(detection.router, prefix="/api/detection", tags=["Detection Rules"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Attack Simulation"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(users_router.router, prefix="/api/users", tags=["User Management"])
app.include_router(ws_router.router, prefix="/api/ws", tags=["WebSocket"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Enhanced health check with DB and Redis connectivity."""
    health = {
        "status": "operational",
        "service": "SOCForge API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": (datetime.now(timezone.utc) - _start_time).total_seconds(),
    }

    # DB check
    try:
        from app.database import async_session
        async with async_session() as session:
            await session.execute(__import__("sqlalchemy").text("SELECT 1"))
        health["database"] = "connected"
    except Exception as e:
        health["database"] = f"error: {str(e)}"
        health["status"] = "degraded"

    # Redis check
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
        health["redis"] = "connected"
    except Exception:
        health["redis"] = "unavailable"

    return health


from starlette.responses import PlainTextResponse

@app.get("/metrics", tags=["Observability"], response_class=PlainTextResponse)
async def prometheus_metrics():
    """Prometheus-compatible metrics endpoint."""
    return PlainTextResponse(get_metrics_text(), media_type="text/plain")


@app.get("/api/metrics", tags=["Observability"])
async def get_metrics():
    """Basic observability metrics endpoint."""
    from sqlalchemy import select, func
    from app.database import async_session
    from app.models.event import Event
    from app.models.alert import Alert
    from app.models.incident import Incident
    from app.models.detection_rule import DetectionRule
    from app.models.user import User

    async with async_session() as db:
        total_events = (await db.execute(select(func.count(Event.id)))).scalar() or 0
        total_alerts = (await db.execute(select(func.count(Alert.id)))).scalar() or 0
        open_alerts = (await db.execute(select(func.count(Alert.id)).where(Alert.status == "open"))).scalar() or 0
        total_incidents = (await db.execute(select(func.count(Incident.id)))).scalar() or 0
        active_rules = (await db.execute(select(func.count(DetectionRule.id)).where(DetectionRule.enabled == True))).scalar() or 0
        total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0

    return {
        "uptime_seconds": (datetime.now(timezone.utc) - _start_time).total_seconds(),
        "total_events": total_events,
        "total_alerts": total_alerts,
        "open_alerts": open_alerts,
        "total_incidents": total_incidents,
        "active_detection_rules": active_rules,
        "total_users": total_users,
    }
