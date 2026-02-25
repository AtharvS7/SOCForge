"""Alert management endpoints."""
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.alert import Alert
from app.schemas import AlertResponse, AlertUpdate
from app.utils.security import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=list[AlertResponse])
async def list_alerts(
    severity: str = Query(None),
    status: str = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Alert).order_by(desc(Alert.created_at))
    if severity:
        query = query.where(Alert.severity == severity)
    if status:
        query = query.where(Alert.status == status)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()
    return [AlertResponse.model_validate(a) for a in alerts]


@router.get("/stats")
async def alert_stats(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(Alert.id)))).scalar() or 0
    open_count = (await db.execute(select(func.count(Alert.id)).where(Alert.status == "open"))).scalar() or 0
    critical = (await db.execute(select(func.count(Alert.id)).where(Alert.severity == "critical"))).scalar() or 0
    high = (await db.execute(select(func.count(Alert.id)).where(Alert.severity == "high"))).scalar() or 0
    fp = (await db.execute(select(func.count(Alert.id)).where(Alert.is_false_positive == True))).scalar() or 0

    return {
        "total": total,
        "open": open_count,
        "critical": critical,
        "high": high,
        "false_positives": fp,
        "false_positive_rate": round(fp / total * 100, 2) if total else 0,
    }


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: UUID,
    data: AlertUpdate,
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if data.status:
        alert.status = data.status
        if data.status == "resolved":
            alert.resolved_at = datetime.utcnow()
    if data.is_false_positive is not None:
        alert.is_false_positive = data.is_false_positive
        if data.is_false_positive:
            alert.status = "false_positive"
    if data.false_positive_reason:
        alert.false_positive_reason = data.false_positive_reason
    if data.assigned_to:
        alert.assigned_to = data.assigned_to

    alert.updated_at = datetime.utcnow()
    await db.commit()
    return AlertResponse.model_validate(alert)
