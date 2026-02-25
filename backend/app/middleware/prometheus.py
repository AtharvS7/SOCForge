"""Prometheus metrics middleware for SOCForge.

Exposes /metrics in Prometheus text format with:
- HTTP request count by method/path/status
- Request latency histogram
- Active connections gauge
"""
import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse

logger = logging.getLogger("socforge.metrics")

# Metrics storage
_request_count: dict[str, int] = defaultdict(int)
_request_latency: dict[str, list] = defaultdict(list)
_error_count: dict[str, int] = defaultdict(int)
_active_connections = 0


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Collect HTTP metrics for Prometheus scraping."""

    async def dispatch(self, request: Request, call_next):
        global _active_connections

        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        _active_connections += 1
        method = request.method
        path = self._normalize_path(request.url.path)
        start = time.perf_counter()

        try:
            response = await call_next(request)
            status = response.status_code
        except Exception:
            status = 500
            raise
        finally:
            _active_connections -= 1
            elapsed = time.perf_counter() - start
            label = f'{method}|{path}|{status}'
            _request_count[label] += 1
            _request_latency[label].append(elapsed)
            if status >= 500:
                _error_count[f'{method}|{path}'] += 1

        return response

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Normalize path to avoid high cardinality (replace UUIDs)."""
        import re
        path = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '{id}', path
        )
        return path


def get_metrics_text() -> str:
    """Generate Prometheus-compatible metrics output."""
    lines = []
    lines.append("# HELP socforge_http_requests_total Total HTTP requests")
    lines.append("# TYPE socforge_http_requests_total counter")
    for label, count in sorted(_request_count.items()):
        method, path, status = label.split("|")
        lines.append(
            f'socforge_http_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}'
        )

    lines.append("")
    lines.append("# HELP socforge_http_request_duration_seconds HTTP request latency")
    lines.append("# TYPE socforge_http_request_duration_seconds summary")
    for label, times in sorted(_request_latency.items()):
        method, path, status = label.split("|")
        if times:
            avg = sum(times) / len(times)
            p95 = sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0]
            lines.append(
                f'socforge_http_request_duration_seconds{{method="{method}",path="{path}",quantile="0.95"}} {p95:.4f}'
            )
            lines.append(
                f'socforge_http_request_duration_seconds_sum{{method="{method}",path="{path}"}} {sum(times):.4f}'
            )
            lines.append(
                f'socforge_http_request_duration_seconds_count{{method="{method}",path="{path}"}} {len(times)}'
            )

    lines.append("")
    lines.append("# HELP socforge_http_errors_total HTTP 5xx errors")
    lines.append("# TYPE socforge_http_errors_total counter")
    for label, count in sorted(_error_count.items()):
        method, path = label.split("|")
        lines.append(f'socforge_http_errors_total{{method="{method}",path="{path}"}} {count}')

    lines.append("")
    lines.append("# HELP socforge_active_connections Current active connections")
    lines.append("# TYPE socforge_active_connections gauge")
    lines.append(f"socforge_active_connections {_active_connections}")

    return "\n".join(lines) + "\n"
