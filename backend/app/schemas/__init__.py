"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# ── Auth Schemas ──
class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: UserRole = UserRole.ANALYST


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Event Schemas ──
class EventCreate(BaseModel):
    event_type: str
    severity: str = "info"
    source_ip: Optional[str] = None
    source_port: Optional[int] = None
    dest_ip: Optional[str] = None
    dest_port: Optional[int] = None
    protocol: Optional[str] = None
    action: Optional[str] = None
    user_account: Optional[str] = None
    hostname: Optional[str] = None
    process_name: Optional[str] = None
    command_line: Optional[str] = None
    raw_log: Optional[str] = None
    normalized_message: Optional[str] = None
    extra_data: Optional[dict] = None


class EventResponse(BaseModel):
    id: UUID
    timestamp: datetime
    event_type: str
    severity: str
    source_ip: Optional[str]
    source_port: Optional[int]
    dest_ip: Optional[str]
    dest_port: Optional[int]
    protocol: Optional[str]
    action: Optional[str]
    user_account: Optional[str]
    hostname: Optional[str]
    process_name: Optional[str]
    normalized_message: Optional[str]
    mitre_tactic: Optional[str]
    mitre_technique: Optional[str]
    mitre_technique_id: Optional[str]
    risk_score: Optional[float]
    simulation_id: Optional[UUID]

    class Config:
        from_attributes = True


class EventBatchCreate(BaseModel):
    events: List[EventCreate]


# ── Alert Schemas ──
class AlertResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    severity: str
    status: str
    source: Optional[str]
    rule_id: Optional[UUID]
    source_ip: Optional[str]
    dest_ip: Optional[str]
    event_count: int
    mitre_tactic: Optional[str]
    mitre_technique: Optional[str]
    mitre_technique_id: Optional[str]
    ioc_indicators: Optional[dict]
    incident_id: Optional[UUID]
    is_false_positive: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    status: Optional[str] = None
    is_false_positive: Optional[bool] = None
    false_positive_reason: Optional[str] = None
    assigned_to: Optional[UUID] = None


# ── Detection Rule Schemas ──
class DetectionRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rule_type: str = "threshold"
    severity: str = "medium"
    event_type_filter: Optional[str] = None
    condition_logic: dict
    threshold_count: Optional[int] = None
    time_window_seconds: Optional[int] = None
    group_by_field: Optional[str] = None
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
    mitre_technique_id: Optional[str] = None
    tags: Optional[List[str]] = None


class DetectionRuleResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    rule_type: str
    severity: str
    enabled: bool
    event_type_filter: Optional[str]
    condition_logic: dict
    threshold_count: Optional[int]
    time_window_seconds: Optional[int]
    group_by_field: Optional[str]
    mitre_tactic: Optional[str]
    mitre_technique: Optional[str]
    mitre_technique_id: Optional[str]
    false_positive_rate: float
    true_positive_count: int
    false_positive_count: int
    total_triggers: int
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DetectionRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    enabled: Optional[bool] = None
    condition_logic: Optional[dict] = None
    threshold_count: Optional[int] = None
    time_window_seconds: Optional[int] = None


# ── Incident Schemas ──
class IncidentResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    severity: str
    status: str
    priority: str
    category: Optional[str]
    alert_count: int
    event_count: int
    affected_hosts: Optional[List[str]]
    affected_users: Optional[List[str]]
    kill_chain_phase: Optional[str]
    mitre_tactics: Optional[List[str]]
    mitre_techniques: Optional[List[str]]
    ioc_summary: Optional[dict]
    timeline: Optional[List[dict]]
    first_seen: Optional[datetime]
    last_seen: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    resolved_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True


class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    assigned_to: Optional[UUID] = None


# ── Report Schemas ──
class ReportCreate(BaseModel):
    title: str
    report_type: str = "incident"
    incident_id: Optional[UUID] = None


class ReportResponse(BaseModel):
    id: UUID
    title: str
    report_type: str
    incident_id: Optional[UUID]
    summary: Optional[str]
    findings: Optional[List[dict]]
    recommendations: Optional[List[str]]
    ioc_list: Optional[List[dict]]
    mitre_mapping: Optional[dict]
    timeline_data: Optional[List[dict]]
    file_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Simulation Schemas ──
class SimulationStart(BaseModel):
    scenario: str = "full_attack_chain"  # full_attack_chain, ssh_brute_force, port_scan, web_attack, lateral_movement
    intensity: str = "medium"  # low, medium, high
    duration_seconds: int = Field(default=60, ge=10, le=600)
    target_network: str = "10.0.1.0/24"
    include_benign_traffic: bool = True


class SimulationStatus(BaseModel):
    simulation_id: UUID
    status: str
    scenario: str
    events_generated: int
    alerts_triggered: int
    started_at: datetime
    progress_percent: float


# ── Dashboard Schemas ──
class DashboardStats(BaseModel):
    total_events: int
    total_alerts: int
    open_alerts: int
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    low_alerts: int
    active_incidents: int
    resolved_incidents: int
    false_positive_rate: float
    detection_rules_active: int
    events_last_24h: int
    alerts_last_24h: int


class MitreCoverage(BaseModel):
    tactic: str
    technique: str
    technique_id: str
    detection_count: int
    alert_count: int


class TimelineEntry(BaseModel):
    timestamp: datetime
    event_type: str
    severity: str
    description: str
    source_ip: Optional[str]
    dest_ip: Optional[str]
    mitre_technique: Optional[str]
