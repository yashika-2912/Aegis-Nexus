from collections import defaultdict, deque
from threading import RLock

from backend.models.event import TimelineEvent
from backend.models.metric import MetricPoint
from backend.models.service import Service


class InMemoryTelemetryStore:
    def __init__(self, history_limit: int = 120, event_limit: int = 80) -> None:
        self._lock = RLock()
        self._services: dict[str, Service] = {}
        self._latest: dict[str, MetricPoint] = {}
        self._history: dict[str, deque[MetricPoint]] = defaultdict(
            lambda: deque(maxlen=history_limit)
        )
        self._events: deque[TimelineEvent] = deque(maxlen=event_limit)

    def upsert_service(self, service: Service) -> None:
        with self._lock:
            self._services[service.id] = service

    def set_metric(self, metric: MetricPoint) -> None:
        with self._lock:
            self._latest[metric.service_id] = metric
            self._history[metric.service_id].append(metric)
            if metric.service_id in self._services:
                service = self._services[metric.service_id]
                service.status = metric.status
                service.available = metric.available

    def add_event(self, event: TimelineEvent) -> None:
        with self._lock:
            self._events.appendleft(event)

    def services(self) -> list[Service]:
        with self._lock:
            return list(self._services.values())

    def latest_metrics(self) -> list[MetricPoint]:
        with self._lock:
            return list(self._latest.values())

    def history(self, service_id: str | None = None) -> dict[str, list[MetricPoint]]:
        with self._lock:
            if service_id:
                return {service_id: list(self._history.get(service_id, []))}
            return {key: list(value) for key, value in self._history.items()}

    def events(self) -> list[TimelineEvent]:
        with self._lock:
            return list(self._events)
