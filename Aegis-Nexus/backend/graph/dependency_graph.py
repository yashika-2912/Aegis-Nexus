"""Fixed dependency graph for Aegis Shop services."""
from __future__ import annotations

from typing import Any

NODES = [
    {"id": "api-gateway", "label": "API Gateway", "type": "gateway", "criticality": "high"},
    {"id": "user-service", "label": "User Service", "type": "service", "criticality": "medium"},
    {"id": "product-service", "label": "Product Service", "type": "service", "criticality": "high"},
    {"id": "order-service", "label": "Order Service", "type": "service", "criticality": "high"},
    {"id": "payment-service", "label": "Payment Service", "type": "service", "criticality": "critical"},
]

EDGES = [
    {"source": "api-gateway", "target": "user-service"},
    {"source": "api-gateway", "target": "product-service"},
    {"source": "api-gateway", "target": "order-service"},
    {"source": "api-gateway", "target": "payment-service"},
    {"source": "order-service", "target": "payment-service"},
]

# Downstream impact map
DOWNSTREAM = {
    "api-gateway": ["user-service", "product-service", "order-service", "payment-service"],
    "product-service": ["api-gateway"],
    "payment-service": ["order-service", "api-gateway"],
    "order-service": ["payment-service", "api-gateway"],
    "user-service": ["api-gateway"],
}


def get_graph(statuses: dict[str, str] | None = None) -> dict[str, Any]:
    statuses = statuses or {}
    nodes = []
    for n in NODES:
        nodes.append({**n, "status": statuses.get(n["id"], "healthy")})
    return {"nodes": nodes, "edges": EDGES}


def blast_radius(failed_service: str) -> list[str]:
    """Services that would be affected if failed_service stays down."""
    affected = set()
    queue = [failed_service]
    while queue:
        svc = queue.pop(0)
        for downstream in DOWNSTREAM.get(svc, []):
            if downstream not in affected:
                affected.add(downstream)
                queue.append(downstream)
    return list(affected)


def critical_path() -> list[str]:
    return ["api-gateway", "product-service", "order-service", "payment-service"]
