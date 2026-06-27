from backend.models.metric import MetricPoint
from backend.utils.health_rules import determine_status, status_score


class HealthService:
    def apply_status(self, metric: MetricPoint) -> MetricPoint:
        metric.status = determine_status(metric)
        return metric

    def system_health(self, metrics: list[MetricPoint]) -> dict[str, int | float]:
        if not metrics:
            return {
                "system_health": 0,
                "healthy_services": 0,
                "warnings": 0,
                "critical": 0,
                "total_services": 0,
            }

        healthy = sum(1 for metric in metrics if metric.status == "Healthy")
        warnings = sum(1 for metric in metrics if metric.status == "Warning")
        critical = sum(1 for metric in metrics if metric.status == "Critical")
        health = round(sum(status_score(metric.status) for metric in metrics) / len(metrics))
        return {
            "system_health": health,
            "healthy_services": healthy,
            "warnings": warnings,
            "critical": critical,
            "total_services": len(metrics),
        }


health_service = HealthService()
