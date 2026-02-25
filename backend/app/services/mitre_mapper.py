"""MITRE ATT&CK mapping service."""

# MITRE ATT&CK Enterprise Tactics and Techniques reference
MITRE_TACTICS = {
    "TA0043": {"name": "Reconnaissance", "description": "Gathering information to plan operations"},
    "TA0001": {"name": "Initial Access", "description": "Gaining entry to the target network"},
    "TA0002": {"name": "Execution", "description": "Running malicious code"},
    "TA0003": {"name": "Persistence", "description": "Maintaining foothold"},
    "TA0004": {"name": "Privilege Escalation", "description": "Gaining higher-level permissions"},
    "TA0005": {"name": "Defense Evasion", "description": "Avoiding detection"},
    "TA0006": {"name": "Credential Access", "description": "Stealing account credentials"},
    "TA0007": {"name": "Discovery", "description": "Learning about the environment"},
    "TA0008": {"name": "Lateral Movement", "description": "Moving through the network"},
    "TA0009": {"name": "Collection", "description": "Gathering data of interest"},
    "TA0011": {"name": "Command and Control", "description": "Communicating with compromised systems"},
    "TA0010": {"name": "Exfiltration", "description": "Stealing data"},
    "TA0040": {"name": "Impact", "description": "Disrupting availability or integrity"},
}

MITRE_TECHNIQUES = {
    "T1595": {"name": "Active Scanning", "tactic": "Reconnaissance", "tactic_id": "TA0043"},
    "T1595.001": {"name": "Scanning IP Blocks", "tactic": "Reconnaissance", "tactic_id": "TA0043"},
    "T1595.002": {"name": "Vulnerability Scanning", "tactic": "Reconnaissance", "tactic_id": "TA0043"},
    "T1046": {"name": "Network Service Discovery", "tactic": "Discovery", "tactic_id": "TA0007"},
    "T1110": {"name": "Brute Force", "tactic": "Credential Access", "tactic_id": "TA0006"},
    "T1110.001": {"name": "Password Guessing", "tactic": "Credential Access", "tactic_id": "TA0006"},
    "T1110.003": {"name": "Password Spraying", "tactic": "Credential Access", "tactic_id": "TA0006"},
    "T1190": {"name": "Exploit Public-Facing Application", "tactic": "Initial Access", "tactic_id": "TA0001"},
    "T1059": {"name": "Command and Scripting Interpreter", "tactic": "Execution", "tactic_id": "TA0002"},
    "T1059.004": {"name": "Unix Shell", "tactic": "Execution", "tactic_id": "TA0002"},
    "T1071": {"name": "Application Layer Protocol", "tactic": "Command and Control", "tactic_id": "TA0011"},
    "T1071.001": {"name": "Web Protocols", "tactic": "Command and Control", "tactic_id": "TA0011"},
    "T1571": {"name": "Non-Standard Port", "tactic": "Command and Control", "tactic_id": "TA0011"},
    "T1573": {"name": "Encrypted Channel", "tactic": "Command and Control", "tactic_id": "TA0011"},
    "T1095": {"name": "Non-Application Layer Protocol", "tactic": "Command and Control", "tactic_id": "TA0011"},
    "T1021": {"name": "Remote Services", "tactic": "Lateral Movement", "tactic_id": "TA0008"},
    "T1021.004": {"name": "SSH", "tactic": "Lateral Movement", "tactic_id": "TA0008"},
    "T1078": {"name": "Valid Accounts", "tactic": "Persistence", "tactic_id": "TA0003"},
    "T1048": {"name": "Exfiltration Over Alternative Protocol", "tactic": "Exfiltration", "tactic_id": "TA0010"},
    "T1041": {"name": "Exfiltration Over C2 Channel", "tactic": "Exfiltration", "tactic_id": "TA0010"},
    "T1018": {"name": "Remote System Discovery", "tactic": "Discovery", "tactic_id": "TA0007"},
    "T1082": {"name": "System Information Discovery", "tactic": "Discovery", "tactic_id": "TA0007"},
    "T1090": {"name": "Proxy", "tactic": "Command and Control", "tactic_id": "TA0011"},
    "T1105": {"name": "Ingress Tool Transfer", "tactic": "Command and Control", "tactic_id": "TA0011"},
    "T1027": {"name": "Obfuscated Files or Information", "tactic": "Defense Evasion", "tactic_id": "TA0005"},
    "T1070": {"name": "Indicator Removal", "tactic": "Defense Evasion", "tactic_id": "TA0005"},
    "T1059.001": {"name": "PowerShell", "tactic": "Execution", "tactic_id": "TA0002"},
}


def get_technique_details(technique_id: str) -> dict:
    """Get MITRE ATT&CK technique details by ID."""
    return MITRE_TECHNIQUES.get(technique_id, {})


def get_tactic_details(tactic_id: str) -> dict:
    """Get MITRE ATT&CK tactic details by ID."""
    return MITRE_TACTICS.get(tactic_id, {})


def map_event_to_mitre(event_type: str, action: str = None, metadata: dict = None) -> dict:
    """Auto-map an event type to MITRE ATT&CK tactic and technique."""
    mapping = {
        "port_scan": {"tactic": "Reconnaissance", "technique": "Active Scanning", "technique_id": "T1595"},
        "ssh_brute_force": {"tactic": "Credential Access", "technique": "Brute Force", "technique_id": "T1110"},
        "ssh_login_failed": {"tactic": "Credential Access", "technique": "Password Guessing", "technique_id": "T1110.001"},
        "ssh_login_success": {"tactic": "Lateral Movement", "technique": "SSH", "technique_id": "T1021.004"},
        "reverse_shell": {"tactic": "Execution", "technique": "Unix Shell", "technique_id": "T1059.004"},
        "c2_beacon": {"tactic": "Command and Control", "technique": "Application Layer Protocol", "technique_id": "T1071"},
        "c2_communication": {"tactic": "Command and Control", "technique": "Web Protocols", "technique_id": "T1071.001"},
        "web_exploit": {"tactic": "Initial Access", "technique": "Exploit Public-Facing Application", "technique_id": "T1190"},
        "sql_injection": {"tactic": "Initial Access", "technique": "Exploit Public-Facing Application", "technique_id": "T1190"},
        "xss_attempt": {"tactic": "Initial Access", "technique": "Exploit Public-Facing Application", "technique_id": "T1190"},
        "path_traversal": {"tactic": "Initial Access", "technique": "Exploit Public-Facing Application", "technique_id": "T1190"},
        "lateral_movement": {"tactic": "Lateral Movement", "technique": "Remote Services", "technique_id": "T1021"},
        "data_exfiltration": {"tactic": "Exfiltration", "technique": "Exfiltration Over C2 Channel", "technique_id": "T1041"},
        "dns_query": {"tactic": "Discovery", "technique": "Remote System Discovery", "technique_id": "T1018"},
        "process_execution": {"tactic": "Execution", "technique": "Command and Scripting Interpreter", "technique_id": "T1059"},
        "privilege_escalation": {"tactic": "Privilege Escalation", "technique": "Valid Accounts", "technique_id": "T1078"},
        "credential_dump": {"tactic": "Credential Access", "technique": "Brute Force", "technique_id": "T1110"},
    }
    return mapping.get(event_type, {"tactic": None, "technique": None, "technique_id": None})


def get_all_tactics() -> list:
    """Return all MITRE ATT&CK tactics."""
    return [{"id": tid, **data} for tid, data in MITRE_TACTICS.items()]


def get_all_techniques() -> list:
    """Return all MITRE ATT&CK techniques."""
    return [{"id": tid, **data} for tid, data in MITRE_TECHNIQUES.items()]


def get_coverage_matrix(detected_techniques: list) -> dict:
    """Generate MITRE ATT&CK coverage matrix based on detected techniques."""
    coverage = {}
    for tactic_id, tactic_data in MITRE_TACTICS.items():
        tactic_techniques = [
            {
                "id": tid,
                "name": tdata["name"],
                "detected": tid in detected_techniques,
            }
            for tid, tdata in MITRE_TECHNIQUES.items()
            if tdata["tactic_id"] == tactic_id
        ]
        coverage[tactic_data["name"]] = {
            "tactic_id": tactic_id,
            "techniques": tactic_techniques,
            "total": len(tactic_techniques),
            "detected": sum(1 for t in tactic_techniques if t["detected"]),
        }
    return coverage
