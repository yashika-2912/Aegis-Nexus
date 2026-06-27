from backend.models.metric import MetricPoint
from backend.models.service import ServiceStatus


def determine_status(metric: MetricPoint) -> ServiceStatus:
    if not metric.available:
        return "Critical"
    if metric.cpu >= 90 or metric.latency >= 2000 or metric.error_rate >= 5:
        return "Critical"
    if metric.cpu >= 70 or metric.latency >= 500 or metric.error_rate >= 1:
        return "Warning"
    return "Healthy"


def status_score(status: ServiceStatus) -> int:
    if status == "Healthy":
        return 100
    if status == "Warning":
        return 55
    return 0
