"""Event ingestion & query endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.event import Event
from app.schemas import EventCreate, EventResponse, EventBatchCreate
from app.services.mitre_mapper import map_event_to_mitre
from app.services.detection_engine import run_detection_engine, seed_detection_rules
from app.services.correlation_engine import correlate_alerts
from app.utils.security import get_current_user, require_role
from app.utils.validators import sanitize_input, validate_ip, validate_severity
from app.models.user import User, UserRole

router = APIRouter()


@router.post("/ingest", response_model=dict)
async def ingest_events(
    data: EventBatchCreate,
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    """Ingest a batch of security events, run detection, and correlate."""
    # Seed rules if needed
    await seed_detection_rules(db)

    created_events = []
    for event_data in data.events:
        # Input sanitization
        severity = validate_severity(event_data.severity) if event_data.severity else "info"
        source_ip = event_data.source_ip if (event_data.source_ip and validate_ip(event_data.source_ip)) else event_data.source_ip
        hostname = sanitize_input(event_data.hostname) if event_data.hostname else None
        command_line = sanitize_input(event_data.command_line) if event_data.command_line else None

        mitre = map_event_to_mitre(event_data.event_type)
        event = Event(
            event_type=sanitize_input(event_data.event_type) if event_data.event_type else event_data.event_type,
            severity=severity,
            source_ip=source_ip,
            source_port=event_data.source_port,
            dest_ip=event_data.dest_ip,
            dest_port=event_data.dest_port,
            protocol=event_data.protocol,
            action=event_data.action,
            user_account=event_data.user_account,
            hostname=hostname,
            process_name=event_data.process_name,
            command_line=command_line,
            raw_log=event_data.raw_log,
            normalized_message=event_data.normalized_message,
            mitre_tactic=mitre.get("tactic"),
            mitre_technique=mitre.get("technique"),
            mitre_technique_id=mitre.get("technique_id"),
            extra_data=event_data.extra_data,
        )
        db.add(event)
        created_events.append(event)

    await db.commit()

    # Run detection engine
    alerts = await run_detection_engine(db, created_events)

    # Run correlation engine
    incidents = []
    if alerts:
        incidents = await correlate_alerts(db, alerts)

    return {
        "events_ingested": len(created_events),
        "alerts_generated": len(alerts),
        "incidents_created": len(incidents),
    }


@router.get("/", response_model=list[EventResponse])
async def list_events(
    event_type: str = Query(None),
    severity: str = Query(None),
    source_ip: str = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Event).order_by(desc(Event.timestamp))
    if event_type:
        query = query.where(Event.event_type == event_type)
    if severity:
        query = query.where(Event.severity == severity)
    if source_ip:
        query = query.where(Event.source_ip == source_ip)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    events = result.scalars().all()
    return [EventResponse.model_validate(e) for e in events]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventResponse.model_validate(event)
