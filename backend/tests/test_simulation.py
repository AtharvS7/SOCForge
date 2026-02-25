"""Simulation engine tests."""
import pytest
from app.services.simulation_engine import get_available_scenarios, _random_ts
from datetime import datetime


class TestSimulationScenarios:
    """Test simulation scenario configuration."""

    def test_scenarios_available(self):
        scenarios = get_available_scenarios()
        assert len(scenarios) == 5

    def test_scenario_ids(self):
        scenarios = get_available_scenarios()
        ids = [s["id"] for s in scenarios]
        assert "full_attack_chain" in ids
        assert "ssh_brute_force" in ids
        assert "port_scan" in ids
        assert "web_attack" in ids
        assert "lateral_movement" in ids

    def test_scenario_required_fields(self):
        required = {"id", "name", "description", "severity", "estimated_events"}
        for scenario in get_available_scenarios():
            missing = required - set(scenario.keys())
            assert not missing, f"Scenario '{scenario['id']}' missing: {missing}"

    def test_scenario_severities_valid(self):
        valid = {"low", "medium", "high", "critical"}
        for scenario in get_available_scenarios():
            assert scenario["severity"] in valid

    def test_scenario_estimated_events_positive(self):
        for scenario in get_available_scenarios():
            assert scenario["estimated_events"] > 0


class TestSimulationHelpers:
    """Test simulation helper functions."""

    def test_random_ts(self):
        base = datetime.utcnow()
        ts = _random_ts(base, 60)
        assert isinstance(ts, datetime)
        assert ts >= base

    def test_random_ts_zero_offset(self):
        base = datetime.utcnow()
        ts = _random_ts(base, 0)
        assert ts == base
