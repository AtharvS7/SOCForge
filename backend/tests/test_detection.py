"""Detection engine tests."""
import pytest
from app.services.detection_engine import BUILT_IN_RULES, _event_matches_rule, _group_events
from app.services.mitre_mapper import map_event_to_mitre, get_coverage_matrix, MITRE_TECHNIQUES


class TestDetectionRules:
    """Test built-in detection rules configuration."""

    def test_built_in_rules_count(self):
        assert len(BUILT_IN_RULES) == 6

    def test_all_rules_have_required_fields(self):
        required = {"name", "rule_type", "severity", "event_type_filter", "mitre_technique_id"}
        for rule in BUILT_IN_RULES:
            missing = required - set(rule.keys())
            assert not missing, f"Rule '{rule['name']}' missing fields: {missing}"

    def test_all_rules_have_mitre_mapping(self):
        for rule in BUILT_IN_RULES:
            assert rule.get("mitre_tactic"), f"Rule '{rule['name']}' missing MITRE tactic"
            assert rule.get("mitre_technique"), f"Rule '{rule['name']}' missing MITRE technique"
            assert rule.get("mitre_technique_id"), f"Rule '{rule['name']}' missing MITRE technique ID"

    def test_severity_values_valid(self):
        valid = {"low", "medium", "high", "critical"}
        for rule in BUILT_IN_RULES:
            assert rule["severity"] in valid, f"Invalid severity '{rule['severity']}' in rule '{rule['name']}'"

    def test_rule_types_valid(self):
        valid = {"threshold", "pattern"}
        for rule in BUILT_IN_RULES:
            assert rule["rule_type"] in valid, f"Invalid rule_type '{rule['rule_type']}' in rule '{rule['name']}'"


class TestMITREMapper:
    """Test MITRE ATT&CK mapping service."""

    def test_ssh_mapping(self):
        result = map_event_to_mitre("ssh_login_failed")
        assert result["tactic"] == "Credential Access"
        assert result["technique_id"] == "T1110.001"

    def test_port_scan_mapping(self):
        result = map_event_to_mitre("port_scan")
        assert result["tactic"] == "Reconnaissance"
        assert result["technique_id"] == "T1595"

    def test_reverse_shell_mapping(self):
        result = map_event_to_mitre("reverse_shell")
        assert result["technique_id"] == "T1059.004"

    def test_c2_beacon_mapping(self):
        result = map_event_to_mitre("c2_beacon")
        assert result["tactic"] == "Command and Control"

    def test_unknown_event_returns_none(self):
        result = map_event_to_mitre("completely_unknown_event")
        assert result.get("tactic") is None

    def test_coverage_matrix_structure(self):
        matrix = get_coverage_matrix(["T1110", "T1595"])
        assert isinstance(matrix, dict)
        for tactic_name, tactic_data in matrix.items():
            assert "tactic_id" in tactic_data
            assert "techniques" in tactic_data
            assert "total" in tactic_data
            assert "detected" in tactic_data

    def test_mitre_techniques_has_entries(self):
        assert len(MITRE_TECHNIQUES) > 0


class TestInputValidation:
    """Test input validation utilities."""

    def test_validate_ip_valid(self):
        from app.utils.validators import validate_ip
        assert validate_ip("192.168.1.1") is True
        assert validate_ip("10.0.0.1") is True
        assert validate_ip("0.0.0.0") is True

    def test_validate_ip_invalid(self):
        from app.utils.validators import validate_ip
        assert validate_ip("999.999.999.999") is False
        assert validate_ip("not_an_ip") is False
        assert validate_ip("") is False

    def test_sanitize_input(self):
        from app.utils.validators import sanitize_input
        assert sanitize_input("normal text") == "normal text"
        assert sanitize_input("text\x00with\x01nulls") == "textwithnulls"
        assert sanitize_input("") == ""

    def test_sanitize_input_none(self):
        from app.utils.validators import sanitize_input
        assert sanitize_input(None) is None

    def test_validate_severity_valid(self):
        from app.utils.validators import validate_severity
        assert validate_severity("critical") == "critical"
        assert validate_severity("INFO") == "info"

    def test_validate_severity_invalid(self):
        from app.utils.validators import validate_severity
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            validate_severity("invalid_severity")
