"""Real remediation actions against Aegis Shop services."""
from __future__ import annotations

import time
from typing import Any

import httpx

SHOP_GATEWAY = "http://localhost:8000"
PRODUCT_SERVICE = "http://localhost:8002"
ORDER_SERVICE = "http://localhost:8003"
PAYMENT_SERVICE = "http://localhost:8004"

ACTION_MAP = {
    "restore_route": {
        "description": "Re-register /products route on Product Service",
        "target": "product-service",
        "endpoint": f"{PRODUCT_SERVICE}/demo/toggle-route",
        "method": "POST",
        "body": {"enabled": True},
    },
    "reset_connection_pool": {
        "description": "Close and recreate Payment DB connection pool",
        "target": "payment-service",
        "endpoint": f"{PAYMENT_SERVICE}/reset",
        "method": "POST",
        "body": None,
    },
    "clear_leak": {
        "description": "Clear in-memory leak list on Order Service",
        "target": "order-service",
        "endpoint": f"{ORDER_SERVICE}/reset",
        "method": "POST",
        "body": None,
    },
    "release_load": {
        "description": "Release held connections from load generator",
        "target": "payment-service",
        "endpoint": f"{PAYMENT_SERVICE}/demo/release-load",
        "method": "POST",
        "body": None,
    },
    "full_reset": {
        "description": "Full shop reset — all services to healthy",
        "target": "api-gateway",
        "endpoint": f"{SHOP_GATEWAY}/reset",
        "method": "POST",
        "body": None,
    },
}

ANOMALY_TO_ACTION = {
    "404_spike": "restore_route",
    "5xx_spike": "reset_connection_pool",
    "latency_degradation": "clear_leak",
}


async def execute_action(action_type: str) -> dict[str, Any]:
    action = ACTION_MAP.get(action_type)
    if not action:
        return {"success": False, "error": f"Unknown action: {action_type}"}

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            kwargs: dict = {}
            if action["body"]:
                kwargs["json"] = action["body"]
            resp = await client.request(action["method"], action["endpoint"], **kwargs)
            return {
                "success": resp.status_code < 400,
                "status_code": resp.status_code,
                "response": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text,
                "action": action_type,
                "target": action["target"],
            }
        except Exception as exc:
            return {"success": False, "error": str(exc), "action": action_type}


async def probe_endpoint(anomaly_type: str) -> dict[str, Any]:
    """Call a real Shop endpoint without remediation side effects."""
    endpoints = {
        "404_spike": ("GET", f"{SHOP_GATEWAY}/products"),
        "5xx_spike": ("POST", f"{SHOP_GATEWAY}/checkout/buy-now", {
            "product_id": "prod-1", "product_name": "Aegis Shield Pro",
            "price": 149.99, "quantity": 1, "user_email": "verify@aegis.shop",
        }),
        "latency_degradation": ("GET", f"{SHOP_GATEWAY}/orders"),
    }
    spec = endpoints.get(anomaly_type, ("GET", f"{SHOP_GATEWAY}/health"))
    method, url = spec[0], spec[1]
    body = spec[2] if len(spec) > 2 else None

    async with httpx.AsyncClient(timeout=8.0) as client:
        start = time.perf_counter()
        try:
            kwargs = {"json": body} if body else {}
            resp = await client.request(method, url, **kwargs)
            latency = (time.perf_counter() - start) * 1000
            return {
                "endpoint": url,
                "status_code": resp.status_code,
                "latency_ms": round(latency, 2),
                "recovered": resp.status_code < 400,
                "body_preview": str(resp.text)[:200],
            }
        except Exception as exc:
            latency = (time.perf_counter() - start) * 1000
            return {
                "endpoint": url,
                "status_code": 0,
                "latency_ms": round(latency, 2),
                "recovered": False,
                "error": str(exc),
            }


async def verify_recovery(anomaly_type: str) -> dict[str, Any]:
    """Re-call real Aegis Shop endpoint to verify recovery."""
    if anomaly_type == "5xx_spike":
        await execute_action("release_load")
    return await probe_endpoint(anomaly_type)
