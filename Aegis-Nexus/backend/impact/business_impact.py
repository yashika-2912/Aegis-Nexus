"""Formula-based business impact from real failed request counts."""
from __future__ import annotations

AVG_ORDER_VALUE = 149.99
UNSEEN_USER_MULTIPLIER = 3.5

PRIORITY_MATRIX = {
    ("P1", "critical"): "P1",
    ("P1", "high"): "P1",
    ("P2", "critical"): "P1",
    ("P2", "high"): "P2",
    ("P3", "critical"): "P2",
    ("P3", "high"): "P3",
    ("P4", "critical"): "P3",
}


def compute_impact(
    failed_requests: int,
    failed_checkouts: int,
    anomaly_type: str,
    affected_service: str,
) -> dict:
    affected_users = int(failed_requests * UNSEEN_USER_MULTIPLIER)
    revenue_at_risk = round(failed_checkouts * AVG_ORDER_VALUE, 2)

    severity_base = "P3"
    if anomaly_type == "5xx_spike" and failed_checkouts > 5:
        severity_base = "P1"
    elif anomaly_type == "5xx_spike":
        severity_base = "P2"
    elif anomaly_type == "404_spike" and failed_requests > 50:
        severity_base = "P2"
    elif anomaly_type == "latency_degradation" and failed_checkouts > 0:
        severity_base = "P2"

    criticality = "critical" if affected_service == "payment-service" else "high"
    if affected_service in ("user-service",):
        criticality = "medium"

    priority = severity_base
    if severity_base == "P2" and criticality == "critical":
        priority = "P1"
    elif severity_base == "P3" and criticality == "critical" and failed_checkouts > 0:
        priority = "P2"

    sla_risk = priority in ("P1", "P2") and failed_checkouts > 0

    return {
        "affected_users_estimate": affected_users,
        "revenue_at_risk": revenue_at_risk,
        "failed_requests": failed_requests,
        "failed_checkouts": failed_checkouts,
        "sla_risk": sla_risk,
        "priority": priority,
        "avg_order_value": AVG_ORDER_VALUE,
        "multiplier": UNSEEN_USER_MULTIPLIER,
    }
