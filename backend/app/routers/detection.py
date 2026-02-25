"""Detection rule management endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.detection_rule import DetectionRule
from app.schemas import DetectionRuleCreate, DetectionRuleResponse, DetectionRuleUpdate
from app.services.detection_engine import seed_detection_rules
from app.utils.security import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/rules", response_model=list[DetectionRuleResponse])
async def list_rules(
    enabled: bool = Query(None),
    severity: str = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await seed_detection_rules(db)
    query = select(DetectionRule).order_by(desc(DetectionRule.created_at))
    if enabled is not None:
        query = query.where(DetectionRule.enabled == enabled)
    if severity:
        query = query.where(DetectionRule.severity == severity)

    result = await db.execute(query)
    rules = result.scalars().all()
    return [DetectionRuleResponse.model_validate(r) for r in rules]


@router.post("/rules", response_model=DetectionRuleResponse)
async def create_rule(
    data: DetectionRuleCreate,
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    rule = DetectionRule(
        name=data.name,
        description=data.description,
        rule_type=data.rule_type,
        severity=data.severity,
        event_type_filter=data.event_type_filter,
        condition_logic=data.condition_logic,
        threshold_count=data.threshold_count,
        time_window_seconds=data.time_window_seconds,
        group_by_field=data.group_by_field,
        mitre_tactic=data.mitre_tactic,
        mitre_technique=data.mitre_technique,
        mitre_technique_id=data.mitre_technique_id,
        tags=data.tags,
        author=user.username,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return DetectionRuleResponse.model_validate(rule)


@router.get("/rules/{rule_id}", response_model=DetectionRuleResponse)
async def get_rule(rule_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DetectionRule).where(DetectionRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Detection rule not found")
    return DetectionRuleResponse.model_validate(rule)


@router.patch("/rules/{rule_id}", response_model=DetectionRuleResponse)
async def update_rule(
    rule_id: UUID,
    data: DetectionRuleUpdate,
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(DetectionRule).where(DetectionRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Detection rule not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)
    return DetectionRuleResponse.model_validate(rule)


@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule_id: UUID,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(DetectionRule).where(DetectionRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Detection rule not found")

    await db.delete(rule)
    await db.commit()
    return {"detail": "Rule deleted"}
