"""Normalized security event model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # ssh_login, port_scan, http_request, etc.
    severity = Column(String(20), default="info", index=True)  # info, low, medium, high, critical
    source_ip = Column(String(45), nullable=True, index=True)
    source_port = Column(Integer, nullable=True)
    dest_ip = Column(String(45), nullable=True, index=True)
    dest_port = Column(Integer, nullable=True)
    protocol = Column(String(20), nullable=True)  # TCP, UDP, ICMP, HTTP
    action = Column(String(50), nullable=True)  # allowed, blocked, failed, success
    user_account = Column(String(100), nullable=True)
    hostname = Column(String(255), nullable=True)
    process_name = Column(String(255), nullable=True)
    command_line = Column(Text, nullable=True)
    raw_log = Column(Text, nullable=True)
    normalized_message = Column(Text, nullable=True)
    mitre_tactic = Column(String(100), nullable=True)
    mitre_technique = Column(String(100), nullable=True)
    mitre_technique_id = Column(String(20), nullable=True)
    geo_country = Column(String(100), nullable=True)
    risk_score = Column(Float, default=0.0)
    extra_data = Column(JSONB, nullable=True)
    simulation_id = Column(UUID(as_uuid=True), nullable=True, index=True)
