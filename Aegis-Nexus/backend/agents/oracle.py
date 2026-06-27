"""Oracle — predicts downstream failures using dependency graph."""
from __future__ import annotations

import time
from typing import Any

from agents.llm import invoke_llm
from graph.dependency_graph import blast_radius, critical_path

FALLBACK = {
    "404_spike": (
        "ORACLE PREDICTION: If unaddressed, product catalog unavailability will persist. "
        "Estimated time-to-full-impact: immediate (already affecting all browse traffic). "
        "Downstream: api-gateway error rate will climb. Checkout unaffected but "
        "conversion funnel blocked at product discovery. Critical path blocked at product-service."
    ),
    "5xx_spike": (
        "ORACLE PREDICTION: Payment failures will cascade to order-service within 2-5 minutes "
        "as pending orders accumulate without payment confirmation. "
        "Estimated revenue impact acceleration: +$150/min at current checkout rate. "
        "Critical path: api-gateway → order-service → payment-service is broken at final step."
    ),
    "latency_degradation": (
        "ORACLE PREDICTION: Order service latency will continue degrading linearly with "
        "each new order (O(n) leak). Estimated time-to-checkout-failure: 10-15 minutes "
        "at current order rate. Payment service may see timeout cascades from slow order creation."
    ),
}


async def run_oracle(state: dict[str, Any]) -> dict[str, Any]:
    anomaly = state.get("anomaly_type", "none")
    affected = state.get("affected_service", "unknown")
    radius = state.get("blast_radius") or blast_radius(affected)
    path = critical_path()

    prompt = f"""You are Oracle, an SRE predictive analysis agent.

Current incident:
- Anomaly: {anomaly}
- Failed service: {affected}
- Blast radius: {', '.join(radius)}
- Critical path: {' → '.join(path)}

Predict what fails next if unaddressed. Give estimated time-to-failure for downstream services.
Reference the dependency graph. 3-4 sentences with specific predictions."""

    output = await invoke_llm(prompt)
    if not output.strip():
        output = FALLBACK.get(anomaly, f"ORACLE: Predicting cascade from {affected}...")

    return {
        **state,
        "oracle_output": output,
        "agent_steps": state.get("agent_steps", []) + [{
            "agent": "Oracle",
            "status": "complete",
            "output": output,
            "timestamp": time.time(),
        }],
    }
