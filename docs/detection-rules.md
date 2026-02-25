# SOCForge Detection Rules Documentation

## Rule Framework

SOCForge uses a configurable detection engine that supports:
- **Threshold-based** detection (count of events in time window)
- **Pattern-based** detection (regex/value matching on event fields)
- **Composite** grouping (group by source_ip, dest_ip, etc.)

---

## Built-in Detection Rules

### 1. SSH Brute Force Detection
- **Severity**: HIGH
- **MITRE**: T1110 — Brute Force (Credential Access)
- **Logic**: ≥5 failed SSH logins from same source IP within 60 seconds
- **SPL Equivalent**: `index=auth sourcetype=ssh action=failed | stats count by src_ip | where count >= 5`
- **False Positive Mitigation**: Whitelist known admin IPs, adjust threshold for environments with auto-retry agents

### 2. Port Scan Detection
- **Severity**: MEDIUM
- **MITRE**: T1595 — Active Scanning (Reconnaissance)
- **Logic**: ≥20 unique destination ports targeted from same IP within 30 seconds
- **SPL Equivalent**: `index=network | stats dc(dest_port) as port_count by src_ip | where port_count >= 20`
- **FP Mitigation**: Exclude vulnerability scanners (Nessus, Qualys) by source IP

### 3. Reverse Shell Detection
- **Severity**: CRITICAL
- **MITRE**: T1059.004 — Unix Shell (Execution)
- **Logic**: Outbound connection with shell process (bash, sh, cmd, nc, powershell)
- **FP Mitigation**: Baseline legitimate admin sessions; alert on unusual source hosts

### 4. C2 Beaconing Detection
- **Severity**: HIGH
- **MITRE**: T1071 — Application Layer Protocol (C2)
- **Logic**: ≥5 connections to same external IP with regular intervals (±30% jitter)
- **FP Mitigation**: Whitelist CDN/update servers; monitor jitter variance

### 5. Web Attack Detection
- **Severity**: HIGH
- **MITRE**: T1190 — Exploit Public-Facing Application (Initial Access)
- **Logic**: Regex match for SQL injection, XSS, path traversal payloads in HTTP logs
- **Pattern**: `union select|<script>|../|etc/passwd|cmd.exe|eval(`
- **FP Mitigation**: Tune for application-specific patterns; exclude health checks

### 6. Lateral Movement Detection
- **Severity**: HIGH
- **MITRE**: T1021 — Remote Services (Lateral Movement)
- **Logic**: ≥3 internal-to-internal connections with auth from same source within 120s
- **FP Mitigation**: Whitelist jump hosts and bastion servers

---

## Custom Rule Creation

Create new rules via the API or the Rule Editor UI:

```json
{
  "name": "Custom HTTP 403 Spike",
  "description": "Detects excessive 403 responses indicating directory enumeration",
  "rule_type": "threshold",
  "severity": "medium",
  "event_type_filter": "http_request",
  "condition_logic": {"field": "action", "operator": "equals", "value": "403"},
  "threshold_count": 50,
  "time_window_seconds": 60,
  "group_by_field": "source_ip",
  "mitre_tactic": "Discovery",
  "mitre_technique_id": "T1083"
}
```
