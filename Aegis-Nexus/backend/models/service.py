from dataclasses import dataclass, field
from typing import Literal

ServiceStatus = Literal["Healthy", "Warning", "Critical"]
ServiceKind = Literal["frontend", "api", "worker", "database"]


@dataclass(slots=True)
class Dependency:
    id: str
    name: str
    status: ServiceStatus = "Healthy"


@dataclass(slots=True)
class Service:
    id: str
    name: str
    kind: ServiceKind
    description: str
    owner: str
    dependencies: list[Dependency] = field(default_factory=list)
    status: ServiceStatus = "Healthy"
    available: bool = True
