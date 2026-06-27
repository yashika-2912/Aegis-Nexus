from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

TwinServiceType = Literal["Gateway", "Microservice", "Database", "Queue", "Cache"]
TwinStatus = Literal["Healthy", "Warning", "Critical", "Affected", "Down"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class TwinServiceNode:
    id: str
    name: str
    type: TwinServiceType
    status: TwinStatus = "Healthy"
    health: int = 100
    last_updated: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class TwinDependencyEdge:
    id: str
    source: str
    target: str
    relationship: str = "DEPENDS_ON"


@dataclass(slots=True)
class ImpactAnalysis:
    failure_origin: str
    affected_services: list[str]
    blast_radius: int
    critical_path: list[str]
    suggested_root_cause: str
