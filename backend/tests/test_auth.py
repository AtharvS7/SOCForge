"""Authentication and RBAC tests."""
import pytest
from tests.conftest import auth_header


class TestAuthRegistration:
    """Test user registration."""

    @pytest.mark.asyncio
    async def test_register_success(self, client):
        res = await client.post("/api/auth/register", json={
            "email": "new@test.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "role": "analyst",
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["role"] == "analyst"

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client, test_admin):
        res = await client.post("/api/auth/register", json={
            "email": "dup@test.com",
            "username": "testadmin",
            "password": "SecurePass123!",
        })
        assert res.status_code == 400

    @pytest.mark.asyncio
    async def test_register_short_password(self, client):
        res = await client.post("/api/auth/register", json={
            "email": "short@test.com",
            "username": "shortpw",
            "password": "short",
        })
        assert res.status_code == 422  # Pydantic validation


class TestAuthLogin:
    """Test login and token generation."""

    @pytest.mark.asyncio
    async def test_login_success(self, client, test_analyst):
        res = await client.post("/api/auth/login", json={
            "username": "testanalyst",
            "password": "TestPass123!",
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["role"] == "analyst"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, test_analyst):
        res = await client.post("/api/auth/login", json={
            "username": "testanalyst",
            "password": "WrongPassword",
        })
        assert res.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        res = await client.post("/api/auth/login", json={
            "username": "nobody",
            "password": "whatever",
        })
        assert res.status_code == 401


class TestAuthMe:
    """Test authenticated user endpoint."""

    @pytest.mark.asyncio
    async def test_get_me(self, client, test_admin, admin_token):
        res = await client.get("/api/auth/me", headers=auth_header(admin_token))
        assert res.status_code == 200
        assert res.json()["username"] == "testadmin"

    @pytest.mark.asyncio
    async def test_get_me_no_token(self, client):
        res = await client.get("/api/auth/me")
        assert res.status_code == 403  # No Bearer token

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client):
        res = await client.get("/api/auth/me", headers=auth_header("invalid_token"))
        assert res.status_code == 401


class TestRBAC:
    """Test role-based access control enforcement."""

    @pytest.mark.asyncio
    async def test_viewer_cannot_ingest_events(self, client, test_viewer, viewer_token):
        res = await client.post(
            "/api/events/ingest",
            json={"events": [{"event_type": "test", "severity": "info"}]},
            headers=auth_header(viewer_token),
        )
        assert res.status_code == 403

    @pytest.mark.asyncio
    async def test_analyst_can_ingest_events(self, client, test_analyst, analyst_token):
        res = await client.post(
            "/api/events/ingest",
            json={"events": [{"event_type": "test_event", "severity": "info"}]},
            headers=auth_header(analyst_token),
        )
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_viewer_cannot_generate_report(self, client, test_viewer, viewer_token):
        res = await client.post(
            "/api/reports/generate",
            json={"title": "Test", "incident_id": "00000000-0000-0000-0000-000000000001"},
            headers=auth_header(viewer_token),
        )
        assert res.status_code == 403

    @pytest.mark.asyncio
    async def test_viewer_cannot_delete_rule(self, client, test_viewer, viewer_token):
        res = await client.delete(
            "/api/detection/rules/00000000-0000-0000-0000-000000000001",
            headers=auth_header(viewer_token),
        )
        assert res.status_code == 403
