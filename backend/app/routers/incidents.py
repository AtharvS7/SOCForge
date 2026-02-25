"""Incident management endpoints."""
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.incident import Incident
from app.schemas import IncidentResponse, IncidentUpdate
from app.services.timeline_service import build_incident_timeline
from app.utils.security import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=list[IncidentResponse])
async def list_incidents(
    status: str = Query(None),
    severity: str = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Incident).order_by(desc(Incident.created_at))
    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(Incident.severity == severity)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    incidents = result.scalars().all()
    return [IncidentResponse.model_validate(i) for i in incidents]


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse.model_validate(incident)


@router.get("/{incident_id}/timeline")
async def get_incident_timeline(
    incident_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    timeline = await build_incident_timeline(db, incident_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="Incident not found or no timeline data")
    return timeline


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    data: IncidentUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if data.status:
        incident.status = data.status
        if data.status in ["resolved", "closed"]:
            incident.resolved_at = datetime.utcnow()
    if data.priority:
        incident.priority = data.priority
    if data.notes:
        incident.notes = data.notes
    if data.assigned_to:
        incident.assigned_to = data.assigned_to

    incident.updated_at = datetime.utcnow()
    await db.commit()
    return IncidentResponse.model_validate(incident)
