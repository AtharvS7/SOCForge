"""Authentication service."""
from datetime import datetime
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.security import hash_password, verify_password, create_access_token


async def register_user(db: AsyncSession, email: str, username: str, password: str, full_name: str = None, role: str = "analyst") -> User:
    """Register a new user."""
    # Check if user exists
    result = await db.execute(
        select(User).where(or_(User.email == email, User.username == username))
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("User with this email or username already exists")

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        full_name=full_name,
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> tuple:
    """Authenticate user and return (user, token)."""
    result = await db.execute(
        select(User).where(or_(User.username == username, User.email == username))
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")

    if not user.is_active:
        raise ValueError("Account is disabled")

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role.value if hasattr(user.role, 'value') else user.role})
    return user, token
