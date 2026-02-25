"""User management endpoints (Admin only)."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas import UserResponse
from app.utils.security import require_role

router = APIRouter()


class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
    full_name: Optional[str] = None


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int


@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 50,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """List all users (admin only)."""
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    )
    users = result.scalars().all()

    count_result = await db.execute(select(func.count(User.id)))
    total = count_result.scalar()

    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific user by ID (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(target)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Update a user's role or active status (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent self-demotion
    if target.id == user.id and data.role and data.role != "admin":
        raise HTTPException(status_code=400, detail="Cannot demote yourself")

    if data.role is not None:
        valid_roles = ["admin", "analyst", "viewer"]
        if data.role not in valid_roles:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role. Must be one of: {valid_roles}",
            )
        target.role = data.role

    if data.is_active is not None:
        # Prevent self-deactivation
        if target.id == user.id and not data.is_active:
            raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
        target.is_active = data.is_active

    if data.full_name is not None:
        target.full_name = data.full_name

    await db.commit()
    await db.refresh(target)
    return UserResponse.model_validate(target)


@router.delete("/{user_id}")
async def deactivate_user(
    user_id: UUID,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a user account (admin only). Does not delete data."""
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    target.is_active = False
    await db.commit()
    return {"detail": f"User {target.username} deactivated", "user_id": str(user_id)}
