"""Healer — proposes and executes remediation."""
from __future__ import annotations

import time
from typing import Any

from agents.llm import invoke_llm
from remediation.actions import ACTION_MAP, ANOMALY_TO_ACTION

FALLBACK = {
    "404_spike": (
        "HEALER RECOMMENDATION: Action — Restore Route on product-service. "
        "Risk score: 0.15 (low). Confidence: 0.95. "
        "Re-register the /products endpoint by toggling route flag to enabled. "
        "Expected recovery: immediate. No data loss risk."
    ),
    "5xx_spike": (
        "HEALER RECOMMENDATION: Action — Reset Connection Pool on payment-service. "
        "Risk score: 0.25 (low-medium). Confidence: 0.92. "
        "Close and recreate the SQLite connection pool, release held connections. "
        "Expected recovery: 2-4 seconds. In-flight payments may need retry."
    ),
    "latency_degradation": (
        "HEALER RECOMMENDATION: Action — Clear Leak on order-service. "
        "Risk score: 0.20 (low). Confidence: 0.90. "
        "Clear the in-memory leaked order list and reset order state. "
        "Expected recovery: immediate latency normalization."
    ),
}


async def run_healer(state: dict[str, Any]) -> dict[str, Any]:
    anomaly = state.get("anomaly_type", "none")
    affected = state.get("affected_service", "unknown")
    action_type = ANOMALY_TO_ACTION.get(anomaly, "full_reset")
    action_info = ACTION_MAP.get(action_type, {})

    prompt = f"""You are Healer, an SRE autonomous remediation agent.

Incident summary:
- Anomaly: {anomaly}
- Affected service: {affected}
- Root cause: {state.get('root_cause', 'unknown')}

Recommended action: {action_info.get('description', action_type)}
Target: {action_info.get('target', affected)}

Propose the remediation with risk score (0-1), confidence (0-1), and expected recovery time.
3-4 sentences. Be specific about the action."""

    output = await invoke_llm(prompt)
    if not output.strip():
        output = FALLBACK.get(anomaly, f"HEALER: Recommend {action_type} on {affected}")

    risk = {"404_spike": 0.15, "5xx_spike": 0.25, "latency_degradation": 0.20}.get(anomaly, 0.3)
    confidence = {"404_spike": 0.95, "5xx_spike": 0.92, "latency_degradation": 0.90}.get(anomaly, 0.8)

    return {
        **state,
        "healer_output": output,
        "recommended_action": action_type,
        "action_target": action_info.get("target", affected),
        "risk_score": risk,
        "confidence": confidence,
        "agent_steps": state.get("agent_steps", []) + [{
            "agent": "Healer",
            "status": "complete",
            "output": output,
            "timestamp": time.time(),
            "metadata": {"action": action_type, "risk": risk, "confidence": confidence},
        }],
    }
