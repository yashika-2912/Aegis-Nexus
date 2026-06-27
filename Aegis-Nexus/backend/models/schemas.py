from pydantic import BaseModel
from typing import Any, Optional
from enum import Enum


class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    DOWN = "down"


class AnomalyType(str, Enum):
    ERROR_SPIKE_404 = "404_spike"
    ERROR_SPIKE_5XX = "5xx_spike"
    LATENCY_DEGRADATION = "latency_degradation"
    NONE = "none"


class ServiceState(BaseModel):
    name: str
    status: ServiceStatus = ServiceStatus.HEALTHY
    error_rate: float = 0.0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    total_requests: int = 0
    error_count: int = 0
    last_status_code: Optional[int] = None
    logs: list[str] = []


class AgentStep(BaseModel):
    agent: str
    status: str  # running | complete | error
    output: str = ""
    timestamp: float = 0.0
    metadata: dict[str, Any] = {}


class RemediationAction(BaseModel):
    action_type: str
    target_service: str
    description: str
    risk_score: float
    confidence: float
    auto_approved: bool = False


class IncidentRecord(BaseModel):
    id: Optional[int] = None
    triggered_at: float
    resolved_at: Optional[float] = None
    anomaly_type: str
    affected_service: str
    root_cause: str
    action_taken: str
    recovery_time_ms: Optional[float] = None
    outcome: str = "pending"
    failed_requests: int = 0
    failed_checkouts: int = 0
    severity: str = "P3"
    agent_outputs: dict[str, str] = {}


class BusinessImpact(BaseModel):
    affected_users_estimate: int
    revenue_at_risk: float
    failed_requests: int
    failed_checkouts: int
    sla_risk: bool
    priority: str
    executive_summary: str = ""


class VerificationResult(BaseModel):
    endpoint: str
    before_status: int
    after_status: int
    before_latency_ms: float
    after_latency_ms: float
    recovered: bool


class WSEvent(BaseModel):
    type: str
    payload: dict[str, Any] = {}
