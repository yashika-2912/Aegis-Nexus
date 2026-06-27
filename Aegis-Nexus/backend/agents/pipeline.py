"""LangGraph pipeline: Sentinel → Sherlock → Oracle → Healer."""
from __future__ import annotations

import asyncio
import time
from typing import Any, Callable, Awaitable

from agents.sentinel import run_sentinel
from agents.sherlock import run_sherlock
from agents.oracle import run_oracle
from agents.healer import run_healer
from impact.business_impact import compute_impact

# Pipeline state
_pipeline_running = False
_current_incident_id: int | None = None
_on_step: Callable[[dict], Awaitable[None]] | None = None


def set_step_callback(cb: Callable[[dict], Awaitable[None]]) -> None:
    global _on_step
    _on_step = cb


async def _emit_step(step: dict) -> None:
    if _on_step:
        await _on_step(step)


async def run_pipeline(
    anomaly_type: str,
    affected_service: str,
    services: dict[str, Any],
    failed_requests: int = 0,
    failed_checkouts: int = 0,
) -> dict[str, Any]:
    global _pipeline_running, _current_incident_id

    if _pipeline_running:
        return {"status": "already_running"}

    _pipeline_running = True
    state: dict[str, Any] = {
        "anomaly_type": anomaly_type,
        "affected_service": affected_service,
        "services": services,
        "failed_requests": failed_requests,
        "failed_checkouts": failed_checkouts,
        "agent_steps": [],
        "started_at": time.time(),
    }

    agents = [
        ("Sentinel", run_sentinel),
        ("Sherlock", run_sherlock),
        ("Oracle", run_oracle),
        ("Healer", run_healer),
    ]

    try:
        for name, agent_fn in agents:
            await _emit_step({"type": "agent_start", "agent": name, "timestamp": time.time()})
            state = await agent_fn(state)
            last_step = state["agent_steps"][-1]
            await _emit_step({"type": "agent_step", "step": last_step})

        impact = compute_impact(failed_requests, failed_checkouts, anomaly_type, affected_service)
        state["business_impact"] = impact

        from models.db import insert_incident
        _current_incident_id = insert_incident({
            "triggered_at": state["started_at"],
            "anomaly_type": anomaly_type,
            "affected_service": affected_service,
            "root_cause": state.get("root_cause", ""),
            "failed_requests": failed_requests,
            "failed_checkouts": failed_checkouts,
            "severity": impact["priority"],
            "agent_outputs": {
                "sentinel": state.get("sentinel_output", ""),
                "sherlock": state.get("sherlock_output", ""),
                "oracle": state.get("oracle_output", ""),
                "healer": state.get("healer_output", ""),
            },
            "outcome": "pending",
        })
        state["incident_id"] = _current_incident_id

        await _emit_step({"type": "pipeline_complete", "state": _serialize_state(state)})
        return state
    finally:
        _pipeline_running = False


def _serialize_state(state: dict) -> dict:
    return {
        k: v for k, v in state.items()
        if k not in ("services",) or isinstance(v, dict)
    }


async def execute_healing(state: dict) -> dict:
    """Execute Healer's recommended action and verify recovery."""
    from remediation.actions import execute_action, probe_endpoint, verify_recovery
    from models.db import update_incident

    action = state.get("recommended_action", "full_reset")
    anomaly = state.get("anomaly_type", "none")
    incident_id = state.get("incident_id")

    before = await probe_endpoint(anomaly)
    await _emit_step({"type": "verification_before", "result": before})

    start = time.time()
    if anomaly == "5xx_spike":
        await execute_action("release_load")
    result = await execute_action(action)
    await _emit_step({"type": "remediation_executed", "result": result})

    await asyncio.sleep(0.5)
    after = await verify_recovery(anomaly)
    await _emit_step({"type": "verification_after", "result": after})

    recovery_ms = (time.time() - start) * 1000
    outcome = "success" if after.get("recovered") else "failed"

    if incident_id:
        update_incident(incident_id, {
            "resolved_at": time.time(),
            "action_taken": ACTION_LABELS.get(action, action),
            "recovery_time_ms": recovery_ms,
            "outcome": outcome,
        })

    return {
        "action_result": result,
        "before": before,
        "after": after,
        "recovery_time_ms": recovery_ms,
        "outcome": outcome,
    }


ACTION_LABELS = {
    "restore_route": "Restore Route",
    "reset_connection_pool": "Reset Connection Pool",
    "clear_leak": "Clear Leak / Restart Order Service",
    "release_load": "Release Load",
    "full_reset": "Full Reset",
}
