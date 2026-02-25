"""Attack simulation endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import SimulationStart
from app.services.simulation_engine import run_simulation, get_simulation_status, get_available_scenarios
from app.services.detection_engine import run_detection_engine, seed_detection_rules
from app.services.correlation_engine import correlate_alerts
from app.utils.security import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.event import Event
from sqlalchemy import select

router = APIRouter()


@router.get("/scenarios")
async def list_scenarios(user: User = Depends(get_current_user)):
    return get_available_scenarios()


@router.post("/start")
async def start_simulation(
    data: SimulationStart,
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    """Start an attack simulation, then run detection & correlation."""
    # Seed rules
    await seed_detection_rules(db)

    # Run simulation
    result = await run_simulation(
        db=db,
        scenario=data.scenario,
        intensity=data.intensity,
        duration_seconds=data.duration_seconds,
        target_network=data.target_network,
        include_benign=data.include_benign_traffic,
    )

    sim_id = result["simulation_id"]

    # Fetch generated events
    from uuid import UUID as _UUID
    events_result = await db.execute(
        select(Event).where(Event.simulation_id == _UUID(sim_id))
    )
    events = events_result.scalars().all()

    # Run detection on attack events (filter out benign)
    attack_events = [e for e in events if e.severity != "info"]
    alerts = await run_detection_engine(db, attack_events)

    # Correlate alerts
    incidents = []
    if alerts:
        incidents = await correlate_alerts(db, alerts)

    result["alerts_triggered"] = len(alerts)
    result["incidents_created"] = len(incidents)

    return result


@router.get("/status/{sim_id}")
async def check_status(sim_id: str, user: User = Depends(get_current_user)):
    status = get_simulation_status(sim_id)
    if not status:
        return {"simulation_id": sim_id, "status": "not_found"}
    return {"simulation_id": sim_id, **status}
