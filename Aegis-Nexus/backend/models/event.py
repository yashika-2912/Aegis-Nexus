from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

EventType = Literal[
    "SERVICE_STARTED",
    "THRESHOLD_CROSSED",
    "RECOVERY",
    "SERVICE_UNAVAILABLE",
    "TELEMETRY",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class TimelineEvent:
    id: str
    service_id: str
    service_name: str
    type: EventType
    severity: str
    message: str
    timestamp: datetime = field(default_factory=utc_now)
