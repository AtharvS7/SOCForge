"""Report generation service with PDF export."""
import os
import uuid
from datetime import datetime
from typing import Optional
from io import BytesIO
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report
from app.models.incident import Incident
from app.models.alert import Alert
from app.services.timeline_service import build_incident_timeline


async def generate_incident_report(db: AsyncSession, incident_id, title: str, generated_by=None) -> Report:
    """Generate a structured investigation report for an incident."""
    # Fetch incident
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise ValueError("Incident not found")

    # Build timeline
    timeline = await build_incident_timeline(db, incident_id)

    # Get related alerts
    result = await db.execute(
        select(Alert).where(Alert.incident_id == incident_id).order_by(Alert.created_at)
    )
    alerts = result.scalars().all()

    # Build findings
    findings = []
    for alert in alerts:
        findings.append({
            "title": alert.title,
            "severity": alert.severity,
            "description": alert.description,
            "mitre_technique": alert.mitre_technique,
            "mitre_technique_id": alert.mitre_technique_id,
            "source_ip": alert.source_ip,
            "dest_ip": alert.dest_ip,
            "event_count": alert.event_count,
            "timestamp": alert.created_at.isoformat() if alert.created_at else None,
        })

    # Build recommendations
    recommendations = _generate_recommendations(incident, alerts)

    # Build IOC list
    ioc_list = _extract_iocs(incident, alerts)

    # Create report
    report = Report(
        title=title or f"Incident Report: {incident.title}",
        report_type="incident",
        incident_id=incident_id,
        summary=_generate_executive_summary(incident, alerts),
        findings=findings,
        recommendations=recommendations,
        ioc_list=ioc_list,
        mitre_mapping={
            "tactics": incident.mitre_tactics or [],
            "techniques": incident.mitre_techniques or [],
            "kill_chain_phase": incident.kill_chain_phase,
        },
        timeline_data=timeline,
        generated_by=generated_by,
    )

    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


def _generate_executive_summary(incident: Incident, alerts: list) -> str:
    """Generate an executive summary for the report."""
    severity_upper = incident.severity.upper() if incident.severity else "UNKNOWN"
    hosts = ", ".join(incident.affected_hosts[:5]) if incident.affected_hosts else "Unknown"
    tactics = ", ".join(incident.mitre_tactics[:5]) if incident.mitre_tactics else "Unknown"

    return (
        f"EXECUTIVE SUMMARY\n\n"
        f"Incident Severity: {severity_upper}\n"
        f"Status: {incident.status}\n"
        f"Category: {incident.category or 'Multi-stage attack'}\n"
        f"Kill Chain Phase: {incident.kill_chain_phase or 'Unknown'}\n\n"
        f"This incident involves {incident.alert_count} correlated security alerts "
        f"targeting the following hosts: {hosts}.\n\n"
        f"MITRE ATT&CK tactics observed: {tactics}.\n\n"
        f"The attack was first detected at {incident.first_seen} "
        f"and the most recent activity was observed at {incident.last_seen}."
    )


def _generate_recommendations(incident: Incident, alerts: list) -> list:
    """Generate actionable recommendations based on incident findings."""
    recs = [
        "Immediately isolate affected hosts from the network to prevent further lateral movement.",
        "Conduct a thorough forensic investigation on all compromised systems.",
        "Reset credentials for all affected user accounts.",
        "Review and update firewall rules to block identified malicious IP addresses.",
        "Implement enhanced monitoring for the affected network segments.",
    ]

    if incident.category == "brute_force":
        recs.extend([
            "Implement account lockout policies after repeated failed login attempts.",
            "Deploy multi-factor authentication (MFA) for all remote access.",
            "Consider implementing fail2ban or similar automated blocking tools.",
        ])
    elif incident.category == "malware":
        recs.extend([
            "Run full malware scans on all affected and adjacent systems.",
            "Check for persistence mechanisms (cron jobs, startup scripts, registry keys).",
            "Block identified C2 server IPs at the perimeter firewall.",
        ])
    elif incident.category == "data_exfiltration":
        recs.extend([
            "Conduct data loss assessment to determine what data was exfiltrated.",
            "Engage legal team for potential breach notification requirements.",
            "Review DLP policies and implement enhanced data monitoring.",
        ])

    return recs


def _extract_iocs(incident: Incident, alerts: list) -> list:
    """Extract all IOCs from the incident."""
    iocs = []
    seen = set()

    if incident.ioc_summary:
        for ip in incident.ioc_summary.get("ip_addresses", []):
            if ip not in seen:
                iocs.append({"type": "ip", "value": ip, "context": "Involved IP address"})
                seen.add(ip)
        for port in incident.ioc_summary.get("ports", []):
            key = f"port:{port}"
            if key not in seen:
                iocs.append({"type": "port", "value": str(port), "context": "Targeted port"})
                seen.add(key)

    for alert in alerts:
        if alert.ioc_indicators:
            for ip in alert.ioc_indicators.get("source_ips", []):
                if ip not in seen:
                    iocs.append({"type": "ip", "value": ip, "context": f"Source IP from {alert.source}"})
                    seen.add(ip)
            for proc in alert.ioc_indicators.get("processes", []):
                key = f"proc:{proc}"
                if key not in seen:
                    iocs.append({"type": "process", "value": proc, "context": "Suspicious process"})
                    seen.add(key)

    return iocs


def generate_pdf_bytes(report: Report) -> bytes:
    """Generate a PDF report using ReportLab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle("Title", parent=styles["Title"], textColor=HexColor("#0ea5e9"), fontSize=20)
    story.append(Paragraph(report.title, title_style))
    story.append(Spacer(1, 12))

    # Metadata
    story.append(Paragraph(f"<b>Report Type:</b> {report.report_type}", styles["Normal"]))
    story.append(Paragraph(f"<b>Generated:</b> {report.created_at.strftime('%Y-%m-%d %H:%M UTC') if report.created_at else 'N/A'}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Summary
    if report.summary:
        story.append(Paragraph("<b>Executive Summary</b>", styles["Heading2"]))
        for line in report.summary.split("\n"):
            if line.strip():
                story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 12))

    # Findings
    if report.findings:
        story.append(Paragraph("<b>Findings</b>", styles["Heading2"]))
        for i, finding in enumerate(report.findings, 1):
            story.append(Paragraph(f"<b>{i}. {finding.get('title', 'Finding')}</b>", styles["Heading3"]))
            story.append(Paragraph(f"Severity: {finding.get('severity', 'N/A')}", styles["Normal"]))
            if finding.get("description"):
                story.append(Paragraph(finding["description"][:500], styles["Normal"]))
            story.append(Spacer(1, 6))

    # IOCs
    if report.ioc_list:
        story.append(Paragraph("<b>Indicators of Compromise (IOCs)</b>", styles["Heading2"]))
        ioc_data = [["Type", "Value", "Context"]]
        for ioc in report.ioc_list[:20]:
            ioc_data.append([ioc.get("type", ""), ioc.get("value", ""), ioc.get("context", "")])
        table = Table(ioc_data, colWidths=[1 * inch, 2.5 * inch, 3 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#334155")),
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

    # Recommendations
    if report.recommendations:
        story.append(Paragraph("<b>Recommendations</b>", styles["Heading2"]))
        for i, rec in enumerate(report.recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", styles["Normal"]))
        story.append(Spacer(1, 6))

    doc.build(story)
    return buffer.getvalue()
