"""Incident model: aggregates correlated alerts."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False, index=True)
    status = Column(String(30), default="open", index=True)  # open, investigating, contained, resolved, closed
    priority = Column(String(20), default="medium")
    category = Column(String(100), nullable=True)  # brute_force, malware, data_exfil, etc.
    alert_count = Column(Integer, default=0)
    event_count = Column(Integer, default=0)
    affected_hosts = Column(JSONB, nullable=True)  # list of hostnames/IPs
    affected_users = Column(JSONB, nullable=True)  # list of user accounts
    kill_chain_phase = Column(String(100), nullable=True)  # reconnaissance, weaponization, delivery, etc.
    mitre_tactics = Column(JSONB, nullable=True)  # list of tactics observed
    mitre_techniques = Column(JSONB, nullable=True)  # list of techniques observed
    ioc_summary = Column(JSONB, nullable=True)
    timeline = Column(JSONB, nullable=True)  # ordered list of timeline entries
    assigned_to = Column(UUID(as_uuid=True), nullable=True)
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
