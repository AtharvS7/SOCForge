"""IOC Enrichment Service: VirusTotal & AbuseIPDB lookups.

Enriches alerts with external threat intelligence.
Results are cached in-memory to minimize API calls.
All lookups are optional and fail-safe.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import httpx

from app.config import settings

logger = logging.getLogger("socforge.enrichment")

# In-memory cache: {ip: {data, expires_at}}
_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = timedelta(hours=1)


def _get_cached(ip: str) -> Optional[dict]:
    entry = _cache.get(ip)
    if entry and entry["expires_at"] > datetime.utcnow():
        return entry["data"]
    return None


def _set_cache(ip: str, data: dict):
    _cache[ip] = {"data": data, "expires_at": datetime.utcnow() + CACHE_TTL}


class IOCEnrichmentService:
    """Enrich IP addresses with threat intelligence from external APIs."""

    def __init__(self):
        self._vt_enabled = bool(settings.VIRUSTOTAL_API_KEY)
        self._abuseipdb_enabled = bool(settings.ABUSEIPDB_API_KEY)

        if self._vt_enabled:
            logger.info("VirusTotal enrichment enabled")
        if self._abuseipdb_enabled:
            logger.info("AbuseIPDB enrichment enabled")

    async def lookup_virustotal(self, ip: str) -> Optional[dict]:
        """Query VirusTotal for IP reputation."""
        if not self._vt_enabled:
            return None
        cache_key = f"vt:{ip}"
        cached = _get_cached(cache_key)
        if cached:
            return cached
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"https://www.virustotal.com/api/v3/ip_addresses/{ip}",
                    headers={"x-apikey": settings.VIRUSTOTAL_API_KEY},
                )
            if resp.status_code == 200:
                data = resp.json().get("data", {}).get("attributes", {})
                result = {
                    "source": "virustotal",
                    "ip": ip,
                    "reputation": data.get("reputation", 0),
                    "malicious": data.get("last_analysis_stats", {}).get("malicious", 0),
                    "suspicious": data.get("last_analysis_stats", {}).get("suspicious", 0),
                    "harmless": data.get("last_analysis_stats", {}).get("harmless", 0),
                    "country": data.get("country", "unknown"),
                    "as_owner": data.get("as_owner", "unknown"),
                }
                _set_cache(cache_key, result)
                return result
            else:
                logger.warning("VirusTotal returned %d for %s", resp.status_code, ip)
                return None
        except Exception as exc:
            logger.error("VirusTotal lookup failed for %s: %s", ip, exc)
            return None

    async def lookup_abuseipdb(self, ip: str) -> Optional[dict]:
        """Query AbuseIPDB for IP abuse reports."""
        if not self._abuseipdb_enabled:
            return None
        cache_key = f"abuse:{ip}"
        cached = _get_cached(cache_key)
        if cached:
            return cached
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.abuseipdb.com/api/v2/check",
                    params={"ipAddress": ip, "maxAgeInDays": 90},
                    headers={
                        "Key": settings.ABUSEIPDB_API_KEY,
                        "Accept": "application/json",
                    },
                )
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                result = {
                    "source": "abuseipdb",
                    "ip": ip,
                    "abuse_confidence_score": data.get("abuseConfidenceScore", 0),
                    "total_reports": data.get("totalReports", 0),
                    "country_code": data.get("countryCode", "unknown"),
                    "isp": data.get("isp", "unknown"),
                    "is_tor": data.get("isTor", False),
                    "is_whitelisted": data.get("isWhitelisted", False),
                }
                _set_cache(cache_key, result)
                return result
            else:
                logger.warning("AbuseIPDB returned %d for %s", resp.status_code, ip)
                return None
        except Exception as exc:
            logger.error("AbuseIPDB lookup failed for %s: %s", ip, exc)
            return None

    async def enrich_ip(self, ip: str) -> dict:
        """Run all available enrichments for an IP address."""
        result: Dict[str, Any] = {"ip": ip, "enriched": False, "sources": []}

        vt = await self.lookup_virustotal(ip)
        if vt:
            result["virustotal"] = vt
            result["sources"].append("virustotal")
            result["enriched"] = True

        abuse = await self.lookup_abuseipdb(ip)
        if abuse:
            result["abuseipdb"] = abuse
            result["sources"].append("abuseipdb")
            result["enriched"] = True

        # Compute composite threat score (0-100)
        scores = []
        if vt:
            # VT malicious detections → 0-100
            scores.append(min(vt.get("malicious", 0) * 5, 100))
        if abuse:
            scores.append(abuse.get("abuse_confidence_score", 0))

        result["threat_score"] = round(sum(scores) / len(scores), 1) if scores else 0

        return result

    async def enrich_alert(self, alert: Any) -> dict:
        """Enrich an alert's source and destination IPs."""
        results = {}
        src = getattr(alert, "source_ip", None)
        dst = getattr(alert, "dest_ip", None)

        if src:
            results["source_ip_intel"] = await self.enrich_ip(src)
        if dst:
            results["dest_ip_intel"] = await self.enrich_ip(dst)

        return results

    @property
    def is_configured(self) -> bool:
        return self._vt_enabled or self._abuseipdb_enabled


# Module-level singleton
enricher = IOCEnrichmentService()
