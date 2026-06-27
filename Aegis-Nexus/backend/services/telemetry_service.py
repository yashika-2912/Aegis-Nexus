import asyncio
import math
import random
from collections import defaultdict

from opentelemetry import metrics

from backend.models.metric import MetricPoint
from backend.models.service import Dependency, Service
from backend.services.event_service import event_service
from backend.services.health_service import health_service
from backend.storage.in_memory_store import InMemoryTelemetryStore


class TelemetryService:
    def __init__(self, store: InMemoryTelemetryStore) -> None:
        self.store = store
        self._tick = 0
        self._request_counts: dict[str, int] = defaultdict(int)
        self._forced_down: set[str] = set()
        meter = metrics.get_meter("aegis-nexus.phase1")
        self._cpu_counter = meter.create_counter("aegis.service.cpu_samples")
        self._latency_counter = meter.create_counter("aegis.service.latency_samples")

    def register_services(self) -> None:
        services = [
            Service("frontend-service", "Frontend Service", "frontend", "Next.js client edge gateway", "Experience Team"),
            Service("payment-service", "Payment Service", "api", "Payment authorization and transaction capture", "Revenue Platform"),
            Service("order-service", "Order Service", "api", "Order orchestration and checkout workflow", "Commerce Core"),
            Service("user-service", "User Service", "api", "Profile, auth, and account data APIs", "Identity Team"),
            Service("postgres-db", "PostgreSQL Database", "database", "Transactional persistence for orders and users", "Data Platform"),
        ]
        dependency_map = {
            "frontend-service": ["order-service", "user-service"],
            "payment-service": ["postgres-db"],
            "order-service": ["payment-service", "postgres-db"],
            "user-service": ["postgres-db"],
            "postgres-db": [],
        }
        by_id = {service.id: service for service in services}
        for service in services:
            service.dependencies = [
                Dependency(id=dep_id, name=by_id[dep_id].name) for dep_id in dependency_map[service.id]
            ]
            self.store.upsert_service(service)
            event_service.emit_started(self.store, service.id, service.name)

    def force_down(self, service_id: str) -> bool:
        if service_id not in {service.id for service in self.store.services()}:
            return False
        self._forced_down.add(service_id)
        return True

    def recover(self, service_id: str) -> bool:
        if service_id not in {service.id for service in self.store.services()}:
            return False
        self._forced_down.discard(service_id)
        return True

    async def run(self) -> None:
        self.register_services()
        while True:
            self._tick += 1
            for service in self.store.services():
                metric = self._generate_metric(service)
                health_service.apply_status(metric)
                self.store.set_metric(metric)
                event_service.track_status_change(self.store, service.id, service.name, metric)
                self._cpu_counter.add(int(metric.cpu), {"service_id": service.id})
                self._latency_counter.add(int(metric.latency), {"service_id": service.id})
            await asyncio.sleep(1)

    def _generate_metric(self, service: Service) -> MetricPoint:
        request_rate_base = {
            "frontend-service": 125,
            "payment-service": 46,
            "order-service": 68,
            "user-service": 38,
            "postgres-db": 92,
        }[service.id]
        phase = self._tick / 8
        wave = math.sin(phase + len(service.id))
        noise = random.uniform(-4, 4)
        cpu = 38 + (wave * 12) + noise
        memory = 48 + (math.cos(phase / 1.5 + len(service.name)) * 9) + random.uniform(-3, 3)
        latency = 120 + max(wave, 0) * 180 + random.uniform(-18, 28)
        error_rate = max(0, random.gauss(0.22, 0.12))
        request_rate = max(1, request_rate_base + wave * 12 + random.uniform(-7, 7))

        if service.id == "payment-service" and 35 <= self._tick % 75 <= 48:
            cpu += 36
            latency += 520
            error_rate += 1.8
        if service.id == "postgres-db" and 55 <= self._tick % 110 <= 67:
            cpu += 28
            latency += 460
            memory += 18
            error_rate += 1.1

        available = service.id not in self._forced_down
        if not available:
            cpu = 0
            memory = 0
            latency = 2800
            error_rate = 18
            request_rate = 0

        self._request_counts[service.id] += int(request_rate)
        return MetricPoint(
            service_id=service.id,
            cpu=max(0, min(cpu, 100)),
            memory=max(0, min(memory, 100)),
            request_count=self._request_counts[service.id],
            request_rate=request_rate,
            error_rate=max(0, error_rate),
            latency=max(10, latency),
            available=available,
        )
