"""Investigation report model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    report_type = Column(String(50), nullable=False)  # incident, executive, detection_summary
    incident_id = Column(UUID(as_uuid=True), nullable=True)
    summary = Column(Text, nullable=True)
    findings = Column(JSONB, nullable=True)
    recommendations = Column(JSONB, nullable=True)
    ioc_list = Column(JSONB, nullable=True)
    mitre_mapping = Column(JSONB, nullable=True)
    timeline_data = Column(JSONB, nullable=True)
    generated_by = Column(UUID(as_uuid=True), nullable=True)
    file_path = Column(String(500), nullable=True)  # path to generated PDF
    created_at = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSONB, nullable=True)
