"""SIEM Integration Service: Splunk HEC & Elasticsearch connectors.

All integrations are optional and fail-safe — if not configured or
if the external service is unreachable, errors are logged but never
propagate to the caller.
"""
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

import httpx

from app.config import settings

logger = logging.getLogger("socforge.siem")


class SIEMConnector:
    """Manages connections to external SIEM platforms."""

    def __init__(self):
        self._splunk_enabled = bool(settings.SPLUNK_HEC_URL and settings.SPLUNK_HEC_TOKEN)
        self._elastic_enabled = bool(settings.ELASTICSEARCH_URL)

        if self._splunk_enabled:
            logger.info("Splunk HEC connector enabled → %s", settings.SPLUNK_HEC_URL)
        if self._elastic_enabled:
            logger.info("Elasticsearch connector enabled → %s", settings.ELASTICSEARCH_URL)
        if not self._splunk_enabled and not self._elastic_enabled:
            logger.info("No SIEM connectors configured — running standalone")

    # ── Splunk HEC ───────────────────────────────────────────────

    async def export_to_splunk(self, events: List[Dict[str, Any]]) -> bool:
        """Send events to Splunk via HTTP Event Collector."""
        if not self._splunk_enabled:
            return False
        try:
            payload = "\n".join(
                json.dumps({
                    "event": evt,
                    "sourcetype": "socforge:alert",
                    "source": "socforge",
                    "time": evt.get("timestamp", datetime.utcnow().timestamp()),
                })
                for evt in events
            )
            async with httpx.AsyncClient(verify=False, timeout=10) as client:
                resp = await client.post(
                    settings.SPLUNK_HEC_URL,
                    content=payload,
                    headers={
                        "Authorization": f"Splunk {settings.SPLUNK_HEC_TOKEN}",
                        "Content-Type": "application/json",
                    },
                )
            if resp.status_code == 200:
                logger.info("Exported %d events to Splunk", len(events))
                return True
            else:
                logger.warning("Splunk HEC returned %d: %s", resp.status_code, resp.text[:200])
                return False
        except Exception as exc:
            logger.error("Splunk export failed: %s", exc)
            return False

    # ── Elasticsearch ────────────────────────────────────────────

    async def export_to_elasticsearch(
        self, events: List[Dict[str, Any]], index: str = "socforge-alerts"
    ) -> bool:
        """Send events to Elasticsearch via bulk API."""
        if not self._elastic_enabled:
            return False
        try:
            lines: list[str] = []
            for evt in events:
                lines.append(json.dumps({"index": {"_index": index}}))
                lines.append(json.dumps(evt, default=str))
            body = "\n".join(lines) + "\n"

            headers: Dict[str, str] = {"Content-Type": "application/x-ndjson"}
            if settings.ELASTICSEARCH_API_KEY:
                headers["Authorization"] = f"ApiKey {settings.ELASTICSEARCH_API_KEY}"

            async with httpx.AsyncClient(verify=False, timeout=10) as client:
                resp = await client.post(
                    f"{settings.ELASTICSEARCH_URL}/_bulk",
                    content=body,
                    headers=headers,
                )
            if resp.status_code in (200, 201):
                logger.info("Exported %d events to Elasticsearch", len(events))
                return True
            else:
                logger.warning("ES bulk returned %d: %s", resp.status_code, resp.text[:200])
                return False
        except Exception as exc:
            logger.error("Elasticsearch export failed: %s", exc)
            return False

    # ── Unified export ───────────────────────────────────────────

    async def export_alerts(self, alerts: List[Any]) -> Dict[str, bool]:
        """Export alert objects to all configured SIEMs."""
        serialized = []
        for alert in alerts:
            serialized.append({
                "alert_id": str(alert.id) if hasattr(alert, "id") else "unknown",
                "title": getattr(alert, "title", ""),
                "severity": getattr(alert, "severity", ""),
                "source_ip": getattr(alert, "source_ip", ""),
                "dest_ip": getattr(alert, "dest_ip", ""),
                "mitre_tactic": getattr(alert, "mitre_tactic", ""),
                "mitre_technique": getattr(alert, "mitre_technique", ""),
                "event_count": getattr(alert, "event_count", 0),
                "timestamp": datetime.utcnow().isoformat(),
                "source": "socforge",
            })

        results = {
            "splunk": await self.export_to_splunk(serialized),
            "elasticsearch": await self.export_to_elasticsearch(serialized),
        }
        return results

    @property
    def is_configured(self) -> bool:
        return self._splunk_enabled or self._elastic_enabled


# Module-level singleton
siem = SIEMConnector()
