"""Event Correlation Engine: groups related alerts into incidents."""
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, func, and_, or_, Text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.event import Event
from app.models.incident import Incident

logger = logging.getLogger("socforge.correlation")

# Kill chain phases ordered by progression
KILL_CHAIN_PHASES = [
    "reconnaissance",
    "initial_access",
    "execution",
    "persistence",
    "privilege_escalation",
    "defense_evasion",
    "credential_access",
    "discovery",
    "lateral_movement",
    "collection",
    "command_and_control",
    "exfiltration",
    "impact",
]

TACTIC_TO_PHASE = {
    "Reconnaissance": "reconnaissance",
    "Initial Access": "initial_access",
    "Execution": "execution",
    "Persistence": "persistence",
    "Privilege Escalation": "privilege_escalation",
    "Defense Evasion": "defense_evasion",
    "Credential Access": "credential_access",
    "Discovery": "discovery",
    "Lateral Movement": "lateral_movement",
    "Collection": "collection",
    "Command and Control": "command_and_control",
    "Exfiltration": "exfiltration",
    "Impact": "impact",
}


async def correlate_alerts(db: AsyncSession, new_alerts: List[Alert]) -> List[Incident]:
    """Correlate new alerts with existing ones to create/update incidents."""
    created_incidents = []

    # Group alerts by source IP for correlation
    ip_groups = {}
    for alert in new_alerts:
        key = alert.source_ip or "unknown"
        if key not in ip_groups:
            ip_groups[key] = []
        ip_groups[key].append(alert)

    for source_ip, alerts in ip_groups.items():
        if source_ip == "unknown":
            continue

        # Check for existing open incident for this IP
        try:
            result = await db.execute(
                select(Incident).where(
                    and_(
                        Incident.status.in_(["open", "investigating"]),
                        func.cast(Incident.affected_hosts, Text).contains(source_ip),
                    )
                )
            )
            existing_incident = result.scalar_one_or_none()
        except Exception:
            existing_incident = None

        if existing_incident:
            # Update existing incident
            existing_incident.alert_count += len(alerts)
            existing_incident.last_seen = datetime.utcnow()

            # Update MITRE data
            tactics = set(existing_incident.mitre_tactics or [])
            techniques = set(existing_incident.mitre_techniques or [])
            for alert in alerts:
                if alert.mitre_tactic:
                    tactics.add(alert.mitre_tactic)
                if alert.mitre_technique:
                    techniques.add(alert.mitre_technique)
                alert.incident_id = existing_incident.id

            existing_incident.mitre_tactics = list(tactics)
            existing_incident.mitre_techniques = list(techniques)
            existing_incident.kill_chain_phase = _determine_kill_chain_phase(list(tactics))

            # Update severity based on highest alert
            severities = ["low", "medium", "high", "critical"]
            max_sev = max(
                [severities.index(a.severity) for a in alerts if a.severity in severities],
                default=0,
            )
            if severities.index(existing_incident.severity) < max_sev:
                existing_incident.severity = severities[max_sev]

        elif len(alerts) >= 2:
            # Create new incident if enough related alerts
            tactics = list(set(a.mitre_tactic for a in alerts if a.mitre_tactic))
            techniques = list(set(a.mitre_technique for a in alerts if a.mitre_technique))

            incident = Incident(
                title=f"Correlated Attack Activity from {source_ip}",
                description=f"Multiple detection rules triggered for source IP {source_ip}. "
                            f"Alerts: {', '.join(a.source or 'unknown' for a in alerts)}",
                severity=_highest_severity(alerts),
                status="open",
                priority=_calculate_priority(alerts),
                category=_determine_category(alerts),
                alert_count=len(alerts),
                event_count=sum(a.event_count for a in alerts),
                affected_hosts=[source_ip] + list(set(a.dest_ip for a in alerts if a.dest_ip)),
                kill_chain_phase=_determine_kill_chain_phase(tactics),
                mitre_tactics=tactics,
                mitre_techniques=techniques,
                ioc_summary=_aggregate_iocs(alerts),
                first_seen=min(a.created_at for a in alerts),
                last_seen=max(a.created_at for a in alerts),
            )
            db.add(incident)
            await db.flush()

            # Link alerts to incident
            for alert in alerts:
                alert.incident_id = incident.id

            created_incidents.append(incident)

    if created_incidents:
        await db.commit()

    return created_incidents


def _highest_severity(alerts: List[Alert]) -> str:
    severities = ["low", "medium", "high", "critical"]
    max_idx = max(
        [severities.index(a.severity) for a in alerts if a.severity in severities],
        default=1,
    )
    return severities[max_idx]


def _calculate_priority(alerts: List[Alert]) -> str:
    count = len(alerts)
    has_critical = any(a.severity == "critical" for a in alerts)
    if has_critical or count >= 5:
        return "critical"
    elif count >= 3:
        return "high"
    elif count >= 2:
        return "medium"
    return "low"


def _determine_category(alerts: List[Alert]) -> str:
    sources = [a.source for a in alerts if a.source]
    if any("brute" in s.lower() for s in sources):
        return "brute_force"
    if any("reverse" in s.lower() or "shell" in s.lower() for s in sources):
        return "malware"
    if any("exfil" in s.lower() for s in sources):
        return "data_exfiltration"
    if any("lateral" in s.lower() for s in sources):
        return "lateral_movement"
    return "multi_stage_attack"


def _determine_kill_chain_phase(tactics: List[str]) -> str:
    """Determine the furthest kill chain phase based on observed tactics."""
    phases = [TACTIC_TO_PHASE.get(t) for t in tactics if t in TACTIC_TO_PHASE]
    if not phases:
        return "reconnaissance"
    return max(phases, key=lambda p: KILL_CHAIN_PHASES.index(p) if p in KILL_CHAIN_PHASES else 0)


def _aggregate_iocs(alerts: List[Alert]) -> dict:
    """Aggregate IOC indicators from all alerts."""
    all_ips = set()
    all_ports = set()
    all_hosts = set()

    for alert in alerts:
        if alert.ioc_indicators:
            for ip in alert.ioc_indicators.get("source_ips", []):
                all_ips.add(ip)
            for ip in alert.ioc_indicators.get("dest_ips", []):
                all_ips.add(ip)
            for port in alert.ioc_indicators.get("dest_ports", []):
                all_ports.add(port)
            for host in alert.ioc_indicators.get("hostnames", []):
                all_hosts.add(host)

    return {
        "ip_addresses": list(all_ips),
        "ports": list(all_ports),
        "hostnames": list(all_hosts),
        "total_alerts": len(alerts),
    }
