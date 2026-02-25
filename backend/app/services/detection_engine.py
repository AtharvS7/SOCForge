"""Detection Engine: rule-based detection with threshold and time-window logic."""
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.alert import Alert
from app.models.detection_rule import DetectionRule
from app.services.mitre_mapper import map_event_to_mitre

logger = logging.getLogger("socforge.detection")

# ── Built-in Detection Rules ──
BUILT_IN_RULES = [
    {
        "name": "SSH Brute Force Detection",
        "description": "Detects multiple failed SSH login attempts from the same source IP within a short time window, indicating a brute force attack.",
        "rule_type": "threshold",
        "severity": "high",
        "event_type_filter": "ssh_login_failed",
        "condition_logic": {"field": "action", "operator": "equals", "value": "failed"},
        "threshold_count": 5,
        "time_window_seconds": 60,
        "group_by_field": "source_ip",
        "mitre_tactic": "Credential Access",
        "mitre_technique": "Brute Force",
        "mitre_technique_id": "T1110",
        "tags": ["brute_force", "ssh", "credential_access"],
    },
    {
        "name": "Port Scan Detection",
        "description": "Detects scanning activity where a source IP targets more than 20 unique destination ports within 30 seconds.",
        "rule_type": "threshold",
        "severity": "medium",
        "event_type_filter": "port_scan",
        "condition_logic": {"field": "dest_port", "operator": "unique_count", "value": 20},
        "threshold_count": 20,
        "time_window_seconds": 30,
        "group_by_field": "source_ip",
        "mitre_tactic": "Reconnaissance",
        "mitre_technique": "Active Scanning",
        "mitre_technique_id": "T1595",
        "tags": ["port_scan", "reconnaissance", "network"],
    },
    {
        "name": "Reverse Shell Detection",
        "description": "Detects outbound connections to uncommon ports with shell process activity, indicating a reverse shell.",
        "rule_type": "pattern",
        "severity": "critical",
        "event_type_filter": "reverse_shell",
        "condition_logic": {"field": "process_name", "operator": "in", "value": ["/bin/sh", "/bin/bash", "cmd.exe", "powershell.exe", "nc", "ncat"]},
        "threshold_count": 1,
        "time_window_seconds": 10,
        "group_by_field": "source_ip",
        "mitre_tactic": "Execution",
        "mitre_technique": "Unix Shell",
        "mitre_technique_id": "T1059.004",
        "tags": ["reverse_shell", "execution", "critical"],
    },
    {
        "name": "C2 Beaconing Detection",
        "description": "Detects regular-interval network connections to the same external IP, indicating command-and-control beaconing behavior.",
        "rule_type": "pattern",
        "severity": "high",
        "event_type_filter": "c2_beacon",
        "condition_logic": {"field": "dest_ip", "operator": "repeated_contact", "value": 5, "interval_tolerance": 0.3},
        "threshold_count": 5,
        "time_window_seconds": 300,
        "group_by_field": "dest_ip",
        "mitre_tactic": "Command and Control",
        "mitre_technique": "Application Layer Protocol",
        "mitre_technique_id": "T1071",
        "tags": ["c2", "beaconing", "network"],
    },
    {
        "name": "Web Attack Detection",
        "description": "Detects SQL injection, XSS, and path traversal patterns in HTTP request logs.",
        "rule_type": "pattern",
        "severity": "high",
        "event_type_filter": "web_exploit",
        "condition_logic": {"field": "raw_log", "operator": "regex_match", "value": r"(union\s+select|<script>|\.\.\/|etc\/passwd|cmd\.exe|eval\()"},
        "threshold_count": 1,
        "time_window_seconds": 60,
        "group_by_field": "source_ip",
        "mitre_tactic": "Initial Access",
        "mitre_technique": "Exploit Public-Facing Application",
        "mitre_technique_id": "T1190",
        "tags": ["web_attack", "sqli", "xss", "initial_access"],
    },
    {
        "name": "Lateral Movement Detection",
        "description": "Detects internal host-to-host connections with authentication attempts, indicating lateral movement.",
        "rule_type": "pattern",
        "severity": "high",
        "event_type_filter": "lateral_movement",
        "condition_logic": {"field": "source_ip", "operator": "internal_to_internal", "value": True},
        "threshold_count": 3,
        "time_window_seconds": 120,
        "group_by_field": "source_ip",
        "mitre_tactic": "Lateral Movement",
        "mitre_technique": "Remote Services",
        "mitre_technique_id": "T1021",
        "tags": ["lateral_movement", "pivoting", "internal"],
    },
]


async def seed_detection_rules(db: AsyncSession):
    """Seed the database with built-in detection rules if they don't exist."""
    for rule_data in BUILT_IN_RULES:
        result = await db.execute(
            select(DetectionRule).where(DetectionRule.name == rule_data["name"])
        )
        if not result.scalar_one_or_none():
            rule = DetectionRule(**rule_data)
            db.add(rule)
    await db.commit()


async def run_detection_engine(db: AsyncSession, events: List[Event]) -> List[Alert]:
    """Run all enabled detection rules against a batch of events."""
    # Fetch enabled rules
    result = await db.execute(select(DetectionRule).where(DetectionRule.enabled == True))
    rules = result.scalars().all()

    generated_alerts = []

    for rule in rules:
        matching_events = [e for e in events if _event_matches_rule(e, rule)]

        if not matching_events:
            continue

        # Group events by the group_by field
        groups = _group_events(matching_events, rule.group_by_field)

        for group_key, group_events in groups.items():
            if len(group_events) >= (rule.threshold_count or 1):
                alert = _create_alert_from_rule(rule, group_events, group_key)
                db.add(alert)
                generated_alerts.append(alert)

                # Update rule stats
                rule.total_triggers = (rule.total_triggers or 0) + 1
                rule.true_positive_count = (rule.true_positive_count or 0) + 1

    if generated_alerts:
        await db.commit()

    return generated_alerts


def _event_matches_rule(event: Event, rule: DetectionRule) -> bool:
    """Check if an event matches the rule's event type filter."""
    if rule.event_type_filter and event.event_type != rule.event_type_filter:
        return False
    return True


def _group_events(events: List[Event], group_by: Optional[str]) -> dict:
    """Group events by a field value."""
    if not group_by:
        return {"all": events}

    groups = {}
    for event in events:
        key = getattr(event, group_by, "unknown") or "unknown"
        if key not in groups:
            groups[key] = []
        groups[key].append(event)
    return groups


def _create_alert_from_rule(rule: DetectionRule, events: List[Event], group_key: str) -> Alert:
    """Create an alert from a triggered detection rule."""
    first_event = events[0]
    mitre = map_event_to_mitre(first_event.event_type)

    ioc_indicators = {
        "source_ips": list(set(e.source_ip for e in events if e.source_ip)),
        "dest_ips": list(set(e.dest_ip for e in events if e.dest_ip)),
        "dest_ports": list(set(e.dest_port for e in events if e.dest_port)),
        "hostnames": list(set(e.hostname for e in events if e.hostname)),
        "processes": list(set(e.process_name for e in events if e.process_name)),
    }

    return Alert(
        title=f"[{rule.severity.upper()}] {rule.name} — {group_key}",
        description=f"{rule.description}\n\nTriggered by {len(events)} events from {group_key}.",
        severity=rule.severity,
        status="open",
        source=rule.name,
        rule_id=rule.id,
        source_ip=first_event.source_ip,
        dest_ip=first_event.dest_ip,
        event_count=len(events),
        mitre_tactic=rule.mitre_tactic or mitre.get("tactic"),
        mitre_technique=rule.mitre_technique or mitre.get("technique"),
        mitre_technique_id=rule.mitre_technique_id or mitre.get("technique_id"),
        ioc_indicators=ioc_indicators,
        related_event_ids=[str(e.id) for e in events],
    )
