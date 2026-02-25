"""Shared test fixtures for SOCForge backend tests."""
import asyncio
import uuid
from datetime import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event, String, JSON, Text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database import Base, get_db
from app.utils.security import create_access_token, hash_password


# ── SQLite compatibility layer for PostgreSQL-specific types ──
# Models use UUID(as_uuid=True), JSONB, and ARRAY from postgresql dialect.
# We must register type adapters so SQLite can handle them.

from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, ARRAY as PG_ARRAY

# Monkey-patch the PostgreSQL types to fall back to generic types on SQLite
_original_uuid_adapt = PG_UUID.__init__

def _patch_pg_types():
    """Register compile-time adapters for PostgreSQL types → SQLite equivalents."""
    from sqlalchemy.ext.compiler import compiles

    @compiles(PG_UUID, "sqlite")
    def compile_uuid(type_, compiler, **kw):
        return "CHAR(36)"

    @compiles(PG_JSONB, "sqlite")
    def compile_jsonb(type_, compiler, **kw):
        return "TEXT"

_patch_pg_types()


# ── Test Database Setup ──
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_socforge.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create tables before each test, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Clean up test db file
    import os
    try:
        os.remove("./test_socforge.db")
    except FileNotFoundError:
        pass


@pytest_asyncio.fixture
async def db_session():
    """Provide a test database session."""
    async with TestSession() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """Provide an async test client with overridden DB dependency."""
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_admin(db_session):
    """Create and return a test admin user."""
    from app.models.user import User
    user = User(
        id=uuid.uuid4(),
        email="admin@test.com",
        username="testadmin",
        hashed_password=hash_password("TestPass123!"),
        full_name="Test Admin",
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_analyst(db_session):
    """Create and return a test analyst user."""
    from app.models.user import User
    user = User(
        id=uuid.uuid4(),
        email="analyst@test.com",
        username="testanalyst",
        hashed_password=hash_password("TestPass123!"),
        full_name="Test Analyst",
        role="analyst",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_viewer(db_session):
    """Create and return a test viewer user."""
    from app.models.user import User
    user = User(
        id=uuid.uuid4(),
        email="viewer@test.com",
        username="testviewer",
        hashed_password=hash_password("TestPass123!"),
        full_name="Test Viewer",
        role="viewer",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
def admin_token(test_admin):
    """JWT token for admin user."""
    return create_access_token({"sub": str(test_admin.id), "role": "admin"})


@pytest_asyncio.fixture
def analyst_token(test_analyst):
    """JWT token for analyst user."""
    return create_access_token({"sub": str(test_analyst.id), "role": "analyst"})


@pytest_asyncio.fixture
def viewer_token(test_viewer):
    """JWT token for viewer user."""
    return create_access_token({"sub": str(test_viewer.id), "role": "viewer"})


def auth_header(token):
    """Create authorization header dict."""
    return {"Authorization": f"Bearer {token}"}
