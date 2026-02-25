"""Dashboard analytics endpoints."""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.event import Event
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.detection_rule import DetectionRule
from app.schemas import DashboardStats
from app.services.mitre_mapper import get_coverage_matrix
from app.utils.security import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)

    total_events = (await db.execute(select(func.count(Event.id)))).scalar() or 0
    total_alerts = (await db.execute(select(func.count(Alert.id)))).scalar() or 0
    open_alerts = (await db.execute(select(func.count(Alert.id)).where(Alert.status == "open"))).scalar() or 0
    critical_alerts = (await db.execute(select(func.count(Alert.id)).where(Alert.severity == "critical"))).scalar() or 0
    high_alerts = (await db.execute(select(func.count(Alert.id)).where(Alert.severity == "high"))).scalar() or 0
    medium_alerts = (await db.execute(select(func.count(Alert.id)).where(Alert.severity == "medium"))).scalar() or 0
    low_alerts = (await db.execute(select(func.count(Alert.id)).where(Alert.severity == "low"))).scalar() or 0
    active_incidents = (await db.execute(select(func.count(Incident.id)).where(Incident.status.in_(["open", "investigating"])))).scalar() or 0
    resolved_incidents = (await db.execute(select(func.count(Incident.id)).where(Incident.status.in_(["resolved", "closed"])))).scalar() or 0
    fp_count = (await db.execute(select(func.count(Alert.id)).where(Alert.is_false_positive == True))).scalar() or 0
    rules_active = (await db.execute(select(func.count(DetectionRule.id)).where(DetectionRule.enabled == True))).scalar() or 0
    events_24h = (await db.execute(select(func.count(Event.id)).where(Event.timestamp >= last_24h))).scalar() or 0
    alerts_24h = (await db.execute(select(func.count(Alert.id)).where(Alert.created_at >= last_24h))).scalar() or 0

    return DashboardStats(
        total_events=total_events,
        total_alerts=total_alerts,
        open_alerts=open_alerts,
        critical_alerts=critical_alerts,
        high_alerts=high_alerts,
        medium_alerts=medium_alerts,
        low_alerts=low_alerts,
        active_incidents=active_incidents,
        resolved_incidents=resolved_incidents,
        false_positive_rate=round(fp_count / total_alerts * 100, 2) if total_alerts else 0.0,
        detection_rules_active=rules_active,
        events_last_24h=events_24h,
        alerts_last_24h=alerts_24h,
    )


@router.get("/severity-distribution")
async def severity_distribution(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Alert count by severity for charts."""
    results = await db.execute(
        select(Alert.severity, func.count(Alert.id)).group_by(Alert.severity)
    )
    return [{"severity": sev, "count": cnt} for sev, cnt in results.all()]


@router.get("/alert-trend")
async def alert_trend(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Hourly alert counts for the last 24 hours."""
    now = datetime.utcnow()
    data = []
    for i in range(24):
        start = now - timedelta(hours=24 - i)
        end = now - timedelta(hours=23 - i)
        count = (await db.execute(
            select(func.count(Alert.id)).where(and_(Alert.created_at >= start, Alert.created_at < end))
        )).scalar() or 0
        data.append({"hour": start.strftime("%H:00"), "count": count})
    return data


@router.get("/mitre-coverage")
async def mitre_coverage(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """MITRE ATT&CK coverage matrix."""
    result = await db.execute(
        select(Alert.mitre_technique_id).where(Alert.mitre_technique_id.isnot(None)).distinct()
    )
    detected = [r[0] for r in result.all()]
    return get_coverage_matrix(detected)


@router.get("/recent-alerts")
async def recent_alerts(
    limit: int = 10,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Alert).order_by(Alert.created_at.desc()).limit(limit)
    )
    alerts = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "title": a.title,
            "severity": a.severity,
            "status": a.status,
            "source_ip": a.source_ip,
            "mitre_technique": a.mitre_technique,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alerts
    ]


@router.get("/top-attackers")
async def top_attackers(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Top source IPs by alert count."""
    result = await db.execute(
        select(Alert.source_ip, func.count(Alert.id).label("count"))
        .where(Alert.source_ip.isnot(None))
        .group_by(Alert.source_ip)
        .order_by(func.count(Alert.id).desc())
        .limit(10)
    )
    return [{"ip": ip, "alert_count": cnt} for ip, cnt in result.all()]
