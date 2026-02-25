"""Detection rule model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    rule_type = Column(String(50), nullable=False)  # threshold, pattern, anomaly, composite
    severity = Column(String(20), nullable=False, default="medium")
    enabled = Column(Boolean, default=True, index=True)

    # Detection logic
    event_type_filter = Column(String(100), nullable=True)  # which event types to match
    condition_logic = Column(JSONB, nullable=False)  # rule condition parameters
    threshold_count = Column(Integer, nullable=True)  # e.g., >5 events
    time_window_seconds = Column(Integer, nullable=True)  # e.g., within 60 seconds
    group_by_field = Column(String(100), nullable=True)  # e.g., group by source_ip

    # MITRE ATT&CK mapping
    mitre_tactic = Column(String(100), nullable=True)
    mitre_technique = Column(String(100), nullable=True)
    mitre_technique_id = Column(String(20), nullable=True)

    # Tuning
    false_positive_rate = Column(Float, default=0.0)
    true_positive_count = Column(Integer, default=0)
    false_positive_count = Column(Integer, default=0)
    total_triggers = Column(Integer, default=0)

    # Metadata
    author = Column(String(100), default="SOCForge")
    tags = Column(JSONB, nullable=True)
    references = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
