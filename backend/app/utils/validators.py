"""Input validation utilities."""
import re
from fastapi import HTTPException


def validate_ip(ip: str) -> bool:
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(pattern, ip):
        return all(0 <= int(octet) <= 255 for octet in ip.split('.'))
    return False


def validate_severity(severity: str) -> str:
    valid = ["info", "low", "medium", "high", "critical"]
    if severity.lower() not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid severity. Must be one of: {valid}")
    return severity.lower()


def sanitize_input(value: str) -> str:
    """Basic input sanitization to prevent injection."""
    if not value:
        return value
    # Remove null bytes and control characters
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
