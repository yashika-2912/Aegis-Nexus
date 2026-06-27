"""Sentinel — anomaly detection from live telemetry."""
from __future__ import annotations

import time
from typing import Any

from agents.llm import invoke_llm

FALLBACK = {
    "404_spike": (
        "SENTINEL ALERT: 404 error spike detected on product-service. "
        "Error rate exceeded 15% threshold over the last 30 seconds. "
        "Severity: HIGH. Classification: route_missing / deployment_regression."
    ),
    "5xx_spike": (
        "SENTINEL ALERT: 5xx error spike detected on payment-service. "
        "Error rate exceeded 20% threshold. Multiple HTTP 500 responses "
        "observed on POST /payments. Severity: CRITICAL. Classification: infrastructure_failure."
    ),
    "latency_degradation": (
        "SENTINEL ALERT: Latency degradation on order-service. "
        "P95 latency exceeded 500ms threshold (currently degrading). "
        "Severity: MEDIUM-HIGH. Classification: performance_regression / memory_pressure."
    ),
}


async def run_sentinel(state: dict[str, Any]) -> dict[str, Any]:
    anomaly = state.get("anomaly_type", "none")
    services = state.get("services", {})
    affected = state.get("affected_service", "unknown")
    svc_data = services.get(affected, {})

    prompt = f"""You are Sentinel, an SRE anomaly detection agent monitoring Aegis Shop.

Live telemetry for {affected}:
- Error rate: {svc_data.get('error_rate', 0)}%
- Avg latency: {svc_data.get('avg_latency_ms', 0)}ms
- P95 latency: {svc_data.get('p95_latency_ms', 0)}ms
- Total requests: {svc_data.get('total_requests', 0)}
- Error count: {svc_data.get('error_count', 0)}
- Status codes: {svc_data.get('status_codes', {})}

Recent logs:
{chr(10).join(svc_data.get('logs', [])[-10:])}

Detected anomaly type: {anomaly}

Write a concise 3-4 sentence alert describing what you detected, severity, and classification.
Be specific — reference the actual metrics and log lines above."""

    output = await invoke_llm(prompt)
    if not output.strip():
        output = FALLBACK.get(anomaly, f"SENTINEL: Anomaly detected — {anomaly} on {affected}")

    return {
        **state,
        "sentinel_output": output,
        "agent_steps": state.get("agent_steps", []) + [{
            "agent": "Sentinel",
            "status": "complete",
            "output": output,
            "timestamp": time.time(),
        }],
    }
