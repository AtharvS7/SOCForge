"""API endpoint integration tests."""
import pytest
from tests.conftest import auth_header


class TestHealthEndpoint:
    """Test health and metrics endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        res = await client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] in ["operational", "degraded"]
        assert data["service"] == "SOCForge API"
        assert "version" in data
        assert "uptime_seconds" in data

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, client):
        res = await client.get("/api/metrics")
        assert res.status_code == 200
        data = res.json()
        assert "total_events" in data
        assert "total_alerts" in data
        assert "uptime_seconds" in data


class TestDashboardEndpoints:
    """Test dashboard analytics endpoints."""

    @pytest.mark.asyncio
    async def test_dashboard_stats(self, client, test_analyst, analyst_token):
        res = await client.get("/api/dashboard/stats", headers=auth_header(analyst_token))
        assert res.status_code == 200
        data = res.json()
        assert "total_events" in data
        assert "open_alerts" in data
        assert "false_positive_rate" in data

    @pytest.mark.asyncio
    async def test_severity_distribution(self, client, test_analyst, analyst_token):
        res = await client.get("/api/dashboard/severity-distribution", headers=auth_header(analyst_token))
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    @pytest.mark.asyncio
    async def test_alert_trend(self, client, test_analyst, analyst_token):
        res = await client.get("/api/dashboard/alert-trend", headers=auth_header(analyst_token))
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) == 24

    @pytest.mark.asyncio
    async def test_top_attackers(self, client, test_analyst, analyst_token):
        res = await client.get("/api/dashboard/top-attackers", headers=auth_header(analyst_token))
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_dashboard_requires_auth(self, client):
        res = await client.get("/api/dashboard/stats")
        assert res.status_code == 403


class TestAlertEndpoints:
    """Test alert management endpoints."""

    @pytest.mark.asyncio
    async def test_list_alerts_empty(self, client, test_analyst, analyst_token):
        res = await client.get("/api/alerts/", headers=auth_header(analyst_token))
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    @pytest.mark.asyncio
    async def test_alert_stats(self, client, test_analyst, analyst_token):
        res = await client.get("/api/alerts/stats", headers=auth_header(analyst_token))
        assert res.status_code == 200
        data = res.json()
        assert "total" in data
        assert "false_positive_rate" in data

    @pytest.mark.asyncio
    async def test_get_nonexistent_alert(self, client, test_analyst, analyst_token):
        res = await client.get(
            "/api/alerts/00000000-0000-0000-0000-000000000001",
            headers=auth_header(analyst_token),
        )
        assert res.status_code == 404


class TestDetectionRuleEndpoints:
    """Test detection rule CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_list_rules(self, client, test_analyst, analyst_token):
        res = await client.get("/api/detection/rules", headers=auth_header(analyst_token))
        assert res.status_code == 200
        rules = res.json()
        assert isinstance(rules, list)
        # Built-in rules should be seeded
        assert len(rules) >= 6

    @pytest.mark.asyncio
    async def test_create_rule(self, client, test_analyst, analyst_token):
        res = await client.post(
            "/api/detection/rules",
            json={
                "name": "Test Custom Rule",
                "description": "Test rule for CI",
                "rule_type": "threshold",
                "severity": "medium",
                "event_type_filter": "test_event",
                "condition_logic": {"field": "action", "operator": "equals", "value": "failed"},
                "threshold_count": 10,
                "time_window_seconds": 120,
            },
            headers=auth_header(analyst_token),
        )
        assert res.status_code == 200
        data = res.json()
        assert data["name"] == "Test Custom Rule"
        assert data["enabled"] is True

    @pytest.mark.asyncio
    async def test_viewer_cannot_create_rule(self, client, test_viewer, viewer_token):
        res = await client.post(
            "/api/detection/rules",
            json={
                "name": "Viewer Rule",
                "rule_type": "threshold",
                "severity": "low",
                "condition_logic": {},
            },
            headers=auth_header(viewer_token),
        )
        assert res.status_code == 403


class TestIncidentEndpoints:
    """Test incident management endpoints."""

    @pytest.mark.asyncio
    async def test_list_incidents_empty(self, client, test_analyst, analyst_token):
        res = await client.get("/api/incidents/", headers=auth_header(analyst_token))
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    @pytest.mark.asyncio
    async def test_get_nonexistent_incident(self, client, test_analyst, analyst_token):
        res = await client.get(
            "/api/incidents/00000000-0000-0000-0000-000000000001",
            headers=auth_header(analyst_token),
        )
        assert res.status_code == 404


class TestEventEndpoints:
    """Test event ingest and listing."""

    @pytest.mark.asyncio
    async def test_list_events_empty(self, client, test_analyst, analyst_token):
        res = await client.get("/api/events/", headers=auth_header(analyst_token))
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    @pytest.mark.asyncio
    async def test_ingest_events(self, client, test_analyst, analyst_token):
        res = await client.post(
            "/api/events/ingest",
            json={
                "events": [
                    {
                        "event_type": "ssh_login_failed",
                        "severity": "medium",
                        "source_ip": "10.0.0.1",
                        "dest_ip": "10.0.1.10",
                        "dest_port": 22,
                        "action": "failed",
                    }
                ]
            },
            headers=auth_header(analyst_token),
        )
        assert res.status_code == 200
        data = res.json()
        assert data["events_ingested"] == 1


class TestSimulationEndpoints:
    """Test simulation endpoints."""

    @pytest.mark.asyncio
    async def test_list_scenarios(self, client, test_analyst, analyst_token):
        res = await client.get("/api/simulation/scenarios", headers=auth_header(analyst_token))
        assert res.status_code == 200
        scenarios = res.json()
        assert len(scenarios) == 5

    @pytest.mark.asyncio
    async def test_viewer_cannot_start_simulation(self, client, test_viewer, viewer_token):
        res = await client.post(
            "/api/simulation/start",
            json={"scenario": "ssh_brute_force", "intensity": "low", "duration_seconds": 10},
            headers=auth_header(viewer_token),
        )
        assert res.status_code == 403
