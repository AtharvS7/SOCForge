"""Notification Service: Email (SMTP) and Slack webhook alerts.

All channels are optional — unconfigured channels silently no-op.
"""
import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Any

import httpx

from app.config import settings

logger = logging.getLogger("socforge.notifications")


class NotificationService:
    """Send alert/incident notifications via email and Slack."""

    def __init__(self):
        self._smtp_enabled = bool(
            settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD
        )
        self._slack_enabled = bool(settings.SLACK_WEBHOOK_URL)

        if self._smtp_enabled:
            logger.info("SMTP notifications enabled → %s", settings.SMTP_HOST)
        if self._slack_enabled:
            logger.info("Slack notifications enabled")

    # ── Email ────────────────────────────────────────────────────

    async def send_email(
        self,
        subject: str,
        body_html: str,
        recipients: Optional[List[str]] = None,
    ) -> bool:
        """Send an email alert via SMTP."""
        if not self._smtp_enabled:
            return False
        try:
            to_addrs = recipients or [settings.SMTP_USER]
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[SOCForge Alert] {subject}"
            msg["From"] = settings.SMTP_USER
            msg["To"] = ", ".join(to_addrs)
            msg.attach(MIMEText(body_html, "html"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT or 587) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_USER, to_addrs, msg.as_string())

            logger.info("Email sent: %s → %s", subject, to_addrs)
            return True
        except Exception as exc:
            logger.error("Email send failed: %s", exc)
            return False

    # ── Slack ────────────────────────────────────────────────────

    async def send_slack(self, text: str, blocks: Optional[list] = None) -> bool:
        """Send alert to Slack via incoming webhook."""
        if not self._slack_enabled:
            return False
        try:
            payload = {"text": text}
            if blocks:
                payload["blocks"] = blocks

            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    settings.SLACK_WEBHOOK_URL,
                    json=payload,
                )
            if resp.status_code == 200:
                logger.info("Slack notification sent")
                return True
            else:
                logger.warning("Slack returned %d", resp.status_code)
                return False
        except Exception as exc:
            logger.error("Slack send failed: %s", exc)
            return False

    # ── High-level alert notification ────────────────────────────

    async def notify_alert(self, alert: Any) -> dict:
        """Send notifications for a new alert (critical/high only)."""
        severity = getattr(alert, "severity", "").lower()
        if severity not in ("critical", "high"):
            return {"email": False, "slack": False, "reason": "below_threshold"}

        title = getattr(alert, "title", "Unknown Alert")
        src_ip = getattr(alert, "source_ip", "N/A")
        tactic = getattr(alert, "mitre_tactic", "N/A")
        technique = getattr(alert, "mitre_technique", "N/A")

        # Email body
        html = f"""
        <h2 style="color:#dc2626">🚨 SOCForge Alert: {title}</h2>
        <table style="border-collapse:collapse">
            <tr><td><b>Severity</b></td><td style="color:#dc2626">{severity.upper()}</td></tr>
            <tr><td><b>Source IP</b></td><td>{src_ip}</td></tr>
            <tr><td><b>MITRE Tactic</b></td><td>{tactic}</td></tr>
            <tr><td><b>MITRE Technique</b></td><td>{technique}</td></tr>
        </table>
        <p>Review in SOCForge dashboard immediately.</p>
        """

        # Slack message
        slack_text = (
            f"🚨 *SOCForge Alert*: {title}\n"
            f"Severity: `{severity.upper()}` | Source: `{src_ip}`\n"
            f"MITRE: {tactic} / {technique}"
        )

        results = {
            "email": await self.send_email(title, html),
            "slack": await self.send_slack(slack_text),
        }
        return results

    async def notify_incident(self, incident: Any) -> dict:
        """Send notifications for a new incident."""
        title = getattr(incident, "title", "Unknown Incident")
        severity = getattr(incident, "severity", "medium")
        alert_count = getattr(incident, "alert_count", 0)

        html = f"""
        <h2 style="color:#f59e0b">⚠️ SOCForge Incident: {title}</h2>
        <p>Severity: <b>{severity.upper()}</b> | Alerts: <b>{alert_count}</b></p>
        <p>Investigate in SOCForge immediately.</p>
        """
        slack_text = (
            f"⚠️ *SOCForge Incident*: {title}\n"
            f"Severity: `{severity.upper()}` | Correlated alerts: `{alert_count}`"
        )

        return {
            "email": await self.send_email(f"Incident: {title}", html),
            "slack": await self.send_slack(slack_text),
        }

    @property
    def is_configured(self) -> bool:
        return self._smtp_enabled or self._slack_enabled


# Module-level singleton
notifier = NotificationService()
