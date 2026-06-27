from backend.models.event import TimelineEvent
from backend.models.metric import MetricPoint
from backend.models.service import Dependency, Service
from backend.schemas.event_schema import EventSchema
from backend.schemas.metric_schema import MetricSchema
from backend.schemas.service_schema import DependencySchema, ServiceSchema
from backend.utils.timestamps import isoformat


def serialize_dependency(dependency: Dependency) -> DependencySchema:
    return DependencySchema(id=dependency.id, name=dependency.name, status=dependency.status)


def serialize_service(service: Service) -> ServiceSchema:
    return ServiceSchema(
        id=service.id,
        name=service.name,
        kind=service.kind,
        description=service.description,
        owner=service.owner,
        status=service.status,
        available=service.available,
        dependencies=[serialize_dependency(item) for item in service.dependencies],
    )


def serialize_metric(metric: MetricPoint) -> MetricSchema:
    return MetricSchema(
        service_id=metric.service_id,
        timestamp=isoformat(metric.timestamp),
        cpu=round(metric.cpu, 2),
        memory=round(metric.memory, 2),
        request_count=metric.request_count,
        request_rate=round(metric.request_rate, 2),
        error_rate=round(metric.error_rate, 2),
        latency=round(metric.latency, 2),
        status=metric.status,
        available=metric.available,
    )


def serialize_event(event: TimelineEvent) -> EventSchema:
    return EventSchema(
        id=event.id,
        service_id=event.service_id,
        service_name=event.service_name,
        type=event.type,
        severity=event.severity,
        message=event.message,
        timestamp=isoformat(event.timestamp),
    )
