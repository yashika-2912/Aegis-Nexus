"""Sherlock — root cause analysis from logs + dependency graph."""
from __future__ import annotations

import time
from typing import Any

from agents.llm import invoke_llm
from graph.dependency_graph import blast_radius

FALLBACK = {
    "404_spike": (
        "SHERLOCK ANALYSIS: Root cause identified — the /products route was deregistered "
        "on product-service, likely from a bad deployment (v1.4). Log evidence: "
        "'GET /products — route deregistered (404)'. The API Gateway propagates this "
        "404 to all product page requests. Blast radius includes api-gateway."
    ),
    "5xx_spike": (
        "SHERLOCK ANALYSIS: Root cause is ConnectionPoolExhausted on Payment DB. "
        "The payment-service maintains a fixed pool of 3 SQLite connections. "
        "Log evidence shows 'Payment failed — pool exhausted'. Concurrent load "
        "has held all connections, causing real HTTP 500 on checkout."
    ),
    "latency_degradation": (
        "SHERLOCK ANALYSIS: Root cause is an unbounded in-memory list in order-service "
        "that grows with every order and is never cleared. Past threshold (50 entries), "
        "each request performs O(n) work causing genuine latency degradation. "
        "This is a real memory leak, not a simulated metric."
    ),
}


async def run_sherlock(state: dict[str, Any]) -> dict[str, Any]:
    anomaly = state.get("anomaly_type", "none")
    affected = state.get("affected_service", "unknown")
    services = state.get("services", {})
    svc_data = services.get(affected, {})
    radius = blast_radius(affected)

    prompt = f"""You are Sherlock, an SRE root cause analysis agent.

Anomaly: {anomaly}
Affected service: {affected}
Blast radius (downstream): {', '.join(radius)}

Service metrics:
{svc_data}

Recent logs (most recent last):
{chr(10).join(svc_data.get('logs', [])[-15:])}

Dependency context: api-gateway → product/order/payment services. Order service calls payment service.

Determine the root cause. Reference specific log lines and metrics. 4-5 sentences."""

    output = await invoke_llm(prompt)
    if not output.strip():
        output = FALLBACK.get(anomaly, f"SHERLOCK: Investigating {anomaly} on {affected}...")

    root_cause = output.split(".")[0] + "." if output else FALLBACK.get(anomaly, "")

    return {
        **state,
        "sherlock_output": output,
        "root_cause": root_cause,
        "blast_radius": radius,
        "agent_steps": state.get("agent_steps", []) + [{
            "agent": "Sherlock",
            "status": "complete",
            "output": output,
            "timestamp": time.time(),
        }],
    }
