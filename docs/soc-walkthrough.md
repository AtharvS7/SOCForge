# SOC Investigation Walkthrough

## Scenario: Full Attack Chain Detection

This walkthrough demonstrates a complete SOC investigation workflow using SOCForge.

### Step 1: Launch Attack Simulation
1. Navigate to **Attack Simulation** page
2. Select **"Full Attack Chain"** scenario
3. Set intensity to **Medium**, duration to **60 seconds**
4. Enable **"Include Benign Traffic"** for realistic false positive testing
5. Click **Launch Simulation**

### Step 2: Monitor Alerts
1. Navigate to **Alert Monitor** page
2. Observe alerts appearing in real-time
3. Filter by severity: **Critical**, **High**
4. Notice alerts covering multiple MITRE ATT&CK tactics:
   - Reconnaissance (Port Scan — T1595)
   - Credential Access (SSH Brute Force — T1110)
   - Execution (Reverse Shell — T1059.004)
   - Command and Control (Beaconing — T1071)
   - Lateral Movement (Remote Services — T1021)

### Step 3: Investigate Incident
1. Navigate to **Investigation** page
2. Select the automatically created incident
3. Review:
   - **Severity & Status** — Critical, Open
   - **MITRE ATT&CK Mapping** — Multiple tactics identified
   - **IOC Summary** — Attacker IP, C2 server, targeted ports
   - **Attack Timeline** — Chronological reconstruction of all events
   - **Affected Hosts** — All compromised systems

### Step 4: Triage Alerts
1. Return to **Alert Monitor**
2. Identify any benign traffic alerts → Mark as **False Positive**
3. Confirm true positives → Set status to **Investigating** or **Resolved**
4. Note: FP rate updates automatically on detection rules

### Step 5: Generate Report
1. Navigate to **Reports** page
2. Select the incident from the dropdown
3. Click **Generate Report**
4. Review report contents:
   - Executive Summary
   - Findings with severity ratings
   - IOC listing
   - MITRE ATT&CK mapping
   - Recommendations
5. Click **Download PDF** for the printable report

### Step 6: Review Detection Rules
1. Navigate to **Detection Rules** page
2. Review each rule's trigger count and false positive rate
3. Adjust thresholds or time windows as needed
4. Create new rules based on observed attack patterns
