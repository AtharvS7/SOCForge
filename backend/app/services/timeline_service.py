"""Timeline reconstruction service."""
from datetime import datetime
from typing import List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.alert import Alert
from app.models.incident import Incident


async def build_incident_timeline(db: AsyncSession, incident_id) -> list:
    """Reconstruct a chronological timeline for an incident."""
    # Get incident
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        return []

    # Get all alerts for this incident
    result = await db.execute(
        select(Alert).where(Alert.incident_id == incident_id).order_by(Alert.created_at)
    )
    alerts = result.scalars().all()

    # Collect all related event IDs
    event_ids = []
    for alert in alerts:
        if alert.related_event_ids:
            event_ids.extend(alert.related_event_ids)

    # Fetch related events
    timeline_entries = []

    if event_ids:
        from uuid import UUID
        valid_ids = []
        for eid in event_ids:
            try:
                valid_ids.append(UUID(eid) if isinstance(eid, str) else eid)
            except (ValueError, AttributeError):
                pass

        if valid_ids:
            result = await db.execute(
                select(Event).where(Event.id.in_(valid_ids)).order_by(Event.timestamp)
            )
            events = result.scalars().all()

            for event in events:
                timeline_entries.append({
                    "timestamp": event.timestamp.isoformat(),
                    "type": "event",
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "description": event.normalized_message or f"{event.event_type} from {event.source_ip}",
                    "source_ip": event.source_ip,
                    "dest_ip": event.dest_ip,
                    "dest_port": event.dest_port,
                    "mitre_tactic": event.mitre_tactic,
                    "mitre_technique": event.mitre_technique,
                    "mitre_technique_id": event.mitre_technique_id,
                    "risk_score": event.risk_score,
                })

    # Add alert entries
    for alert in alerts:
        timeline_entries.append({
            "timestamp": alert.created_at.isoformat(),
            "type": "alert",
            "event_type": "alert_generated",
            "severity": alert.severity,
            "description": alert.title,
            "source_ip": alert.source_ip,
            "dest_ip": alert.dest_ip,
            "dest_port": None,
            "mitre_tactic": alert.mitre_tactic,
            "mitre_technique": alert.mitre_technique,
            "mitre_technique_id": alert.mitre_technique_id,
            "risk_score": None,
        })

    # Sort by timestamp
    timeline_entries.sort(key=lambda x: x["timestamp"])

    # Update incident timeline
    incident.timeline = timeline_entries
    await db.commit()

    return timeline_entries
