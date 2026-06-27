from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from backend.models.service import ServiceStatus

MetricName = Literal["cpu", "memory", "requests", "latency", "error_rate"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class MetricPoint:
    service_id: str
    timestamp: datetime = field(default_factory=utc_now)
    cpu: float = 0
    memory: float = 0
    request_count: int = 0
    request_rate: float = 0
    error_rate: float = 0
    latency: float = 0
    status: ServiceStatus = "Healthy"
    available: bool = True
