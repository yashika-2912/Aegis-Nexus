from uuid import uuid4

from backend.models.event import TimelineEvent
from backend.models.metric import MetricPoint
from backend.models.service import ServiceStatus
from backend.storage.in_memory_store import InMemoryTelemetryStore


class EventService:
    def __init__(self) -> None:
        self._last_status: dict[str, ServiceStatus] = {}
        self._started: set[str] = set()

    def emit_started(self, store: InMemoryTelemetryStore, service_id: str, service_name: str) -> None:
        if service_id in self._started:
            return
        self._started.add(service_id)
        store.add_event(
            TimelineEvent(
                id=str(uuid4()),
                service_id=service_id,
                service_name=service_name,
                type="SERVICE_STARTED",
                severity="info",
                message=f"{service_name} started telemetry export.",
            )
        )

    def track_status_change(
        self,
        store: InMemoryTelemetryStore,
        service_id: str,
        service_name: str,
        metric: MetricPoint,
    ) -> None:
        previous = self._last_status.get(service_id)
        self._last_status[service_id] = metric.status
        if previous is None or previous == metric.status:
            return

        if metric.status == "Critical" and not metric.available:
            event_type = "SERVICE_UNAVAILABLE"
            severity = "critical"
            message = f"{service_name} is unavailable. Downstream request errors are rising."
        elif metric.status == "Healthy":
            event_type = "RECOVERY"
            severity = "success"
            message = f"{service_name} recovered and returned inside healthy thresholds."
        else:
            event_type = "THRESHOLD_CROSSED"
            severity = "warning" if metric.status == "Warning" else "critical"
            message = (
                f"{service_name} crossed a threshold: CPU {metric.cpu:.0f}%, "
                f"latency {metric.latency:.0f}ms, error rate {metric.error_rate:.1f}%."
            )

        store.add_event(
            TimelineEvent(
                id=str(uuid4()),
                service_id=service_id,
                service_name=service_name,
                type=event_type,
                severity=severity,
                message=message,
            )
        )


event_service = EventService()
