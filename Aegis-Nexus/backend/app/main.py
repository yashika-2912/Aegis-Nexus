"""Aegis Nexus — main FastAPI app with WebSocket and telemetry."""
from __future__ import annotations

import asyncio
import json
import time
from collections import deque
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.pipeline import execute_healing, run_pipeline, set_step_callback
from data.seed_incidents import seed_if_empty
from graph.dependency_graph import get_graph
from graph.twin_service import twin_graph, twin_reset, twin_simulate_failure
from schemas.digital_twin_schema import FailureSimulationRequest, ImpactAnalysisResponse, TwinGraphSchema
from impact.business_impact import compute_impact
from models.db import get_incidents, get_learning_stats, init_db
from remediation.actions import execute_action

SERVICE_NAMES = [
    "api-gateway", "user-service", "product-service",
    "order-service", "payment-service",
]

# In-memory telemetry store
_services: dict[str, dict] = {
    name: {
        "name": name,
        "status": "healthy",
        "error_rate": 0.0,
        "avg_latency_ms": 0.0,
        "p95_latency_ms": 0.0,
        "total_requests": 0,
        "error_count": 0,
        "status_codes": {},
        "logs": [],
        "history": deque(maxlen=60),
    }
    for name in SERVICE_NAMES
}

_ws_clients: list[WebSocket] = []
_incident_window: dict[str, Any] = {
    "active": False,
    "started_at": 0.0,
    "failed_requests": 0,
    "failed_checkouts": 0,
    "anomaly_type": "none",
    "affected_service": "",
}
_pipeline_state: dict | None = None
_anomaly_cooldown = 0.0

# Detection thresholds
THRESHOLDS = {
    "error_rate_5xx": 15.0,
    "error_rate_404": 10.0,
    "latency_p95": 500.0,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seeded = seed_if_empty()
    print(f"Nexus DB initialized. Seeded {seeded} incidents.")
    asyncio.create_task(_health_poller())
    yield


app = FastAPI(title="Aegis Nexus", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def broadcast(event: dict) -> None:
    dead = []
    for ws in _ws_clients:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _ws_clients.remove(ws)


async def _on_pipeline_step(step: dict) -> None:
    await broadcast({"type": "pipeline_event", "payload": step})


set_step_callback(_on_pipeline_step)


def ingest_telemetry(payload: dict) -> None:
    svc = payload.get("service", "unknown")
    if svc not in _services:
        _services[svc] = {"name": svc, "status": "healthy", "logs": [], "history": deque(maxlen=60)}

    if payload.get("type") == "log":
        logs = _services[svc].setdefault("logs", [])
        logs.append(payload["line"])
        if len(logs) > 50:
            _services[svc]["logs"] = logs[-50:]

    elif payload.get("type") == "metric":
        metrics = payload.get("metrics", {})
        status = payload.get("status", 200)
        latency = payload.get("latency_ms", 0)

        _services[svc].update({
            "error_rate": metrics.get("error_rate", 0),
            "avg_latency_ms": metrics.get("avg_latency_ms", 0),
            "p95_latency_ms": metrics.get("p95_latency_ms", 0),
            "total_requests": metrics.get("total_requests", 0),
            "error_count": metrics.get("error_count", 0),
            "status_codes": metrics.get("status_codes", {}),
            "last_status_code": status,
        })

        # Update status
        er = metrics.get("error_rate", 0)
        p95 = metrics.get("p95_latency_ms", 0)
        if er > 30 or status >= 500:
            _services[svc]["status"] = "critical"
        elif er > 15 or p95 > 500:
            _services[svc]["status"] = "degraded"
        elif er > 5 or p95 > 200:
            _services[svc]["status"] = "warning"
        else:
            _services[svc]["status"] = "healthy"

        hist = _services[svc].setdefault("history", deque(maxlen=60))
        hist.append({
            "timestamp": payload.get("timestamp", time.time()),
            "latency_ms": latency,
            "error_rate": er,
            "status": status,
        })

        _track_incident_window(svc, status)
        _check_anomaly(svc)


def _track_incident_window(svc: str, status: int) -> None:
    if status >= 400:
        if not _incident_window["active"]:
            _incident_window["active"] = True
            _incident_window["started_at"] = time.time()
        _incident_window["failed_requests"] += 1
        if status >= 500 and svc in ("payment-service", "api-gateway"):
            _incident_window["failed_checkouts"] += 1


def _detect_anomaly(svc: str) -> tuple[str, str] | None:
    data = _services.get(svc, {})
    codes = data.get("status_codes", {})
    er = data.get("error_rate", 0)
    p95 = data.get("p95_latency_ms", 0)

    count_404 = sum(v for k, v in codes.items() if k == 404 or str(k) == "404")
    count_5xx = sum(v for k, v in codes.items() if str(k).isdigit() and int(k) >= 500)

    if count_404 >= 2 or (er > THRESHOLDS["error_rate_404"] and count_404 > 0):
        return "404_spike", svc if svc == "product-service" else "product-service"
    if count_5xx >= 1 or (er > THRESHOLDS["error_rate_5xx"] and svc == "payment-service"):
        return "5xx_spike", "payment-service"
    if p95 > THRESHOLDS["latency_p95"] and svc == "order-service":
        return "latency_degradation", "order-service"
    if er > THRESHOLDS["error_rate_5xx"]:
        return "5xx_spike", svc
    return None


def _check_anomaly(svc: str) -> None:
    global _anomaly_cooldown
    if time.time() < _anomaly_cooldown:
        return
    result = _detect_anomaly(svc)
    if result:
        anomaly, affected = result
        _incident_window["anomaly_type"] = anomaly
        _incident_window["affected_service"] = affected
        _anomaly_cooldown = time.time() + 30
        asyncio.create_task(_auto_pipeline(anomaly, affected))


async def _auto_pipeline(anomaly: str, affected: str) -> None:
    global _pipeline_state
    await broadcast({"type": "anomaly_detected", "payload": {
        "anomaly_type": anomaly, "affected_service": affected,
    }})
    state = await run_pipeline(
        anomaly, affected, dict(_services),
        _incident_window["failed_requests"],
        _incident_window["failed_checkouts"],
    )
    _pipeline_state = state


async def _health_poller() -> None:
    """Poll shop services for health status."""
    urls = {
        "api-gateway": "http://localhost:8000/health",
        "user-service": "http://localhost:8001/health",
        "product-service": "http://localhost:8002/health",
        "order-service": "http://localhost:8003/health",
        "payment-service": "http://localhost:8004/health",
    }
    while True:
        async with httpx.AsyncClient(timeout=3.0) as client:
            for name, url in urls.items():
                try:
                    r = await client.get(url)
                    data = r.json()
                    status = data.get("status", "healthy")
                    if name in _services:
                        if status in ("critical", "degraded", "warning"):
                            _services[name]["status"] = status
                        elif _services[name].get("error_rate", 0) < 5:
                            _services[name]["status"] = status
                except Exception:
                    if name in _services:
                        _services[name]["status"] = "down"
        await broadcast({"type": "telemetry", "payload": _snapshot()})
        await asyncio.sleep(3)


def _snapshot() -> dict:
    statuses = {k: v.get("status", "healthy") for k, v in _services.items()}
    return {
        "services": {k: {**v, "history": list(v.get("history", []))} for k, v in _services.items()},
        "graph": get_graph(statuses),
        "incident_window": dict(_incident_window),
        "pipeline_state": _pipeline_state is not None,
        "timestamp": time.time(),
    }


# --- API Routes ---

@app.get("/")
async def root():
    return {
        "service": "Aegis Nexus API",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws",
        "incidents": "/api/incidents",
        "services": "/api/services",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "aegis-nexus"}


@app.get("/digital-twin/graph", response_model=TwinGraphSchema)
async def digital_twin_graph():
    return twin_graph()


@app.post("/digital-twin/simulate/failure", response_model=ImpactAnalysisResponse)
async def digital_twin_simulate_failure(payload: FailureSimulationRequest):
    try:
        return twin_simulate_failure(payload.service_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown service") from exc


@app.post("/digital-twin/reset", response_model=TwinGraphSchema)
async def digital_twin_reset():
    return twin_reset()


class TelemetryIngest(BaseModel):
    type: str
    service: str
    line: str | None = None
    level: str | None = None
    status: int | None = None
    latency_ms: float | None = None
    metrics: dict | None = None
    timestamp: float | None = None


@app.post("/api/telemetry/ingest")
async def telemetry_ingest(payload: TelemetryIngest):
    ingest_telemetry(payload.model_dump(exclude_none=True))
    await broadcast({"type": "telemetry", "payload": _snapshot()})
    return {"status": "ok"}


@app.get("/api/services")
async def get_services():
    return _snapshot()


@app.get("/api/incidents")
async def incidents(limit: int = 50):
    return {"incidents": get_incidents(limit)}


@app.get("/api/learning/stats")
async def learning_stats():
    return {"stats": get_learning_stats()}


class HealRequest(BaseModel):
    action: str | None = None


@app.post("/api/heal/execute")
async def heal_execute(req: HealRequest | None = None):
    global _pipeline_state, _incident_window
    if not _pipeline_state:
        return {"error": "No active pipeline — trigger reanalyze first"}
    result = await execute_healing(_pipeline_state)
    _incident_window = {"active": False, "started_at": 0, "failed_requests": 0,
                        "failed_checkouts": 0, "anomaly_type": "none", "affected_service": ""}
    await broadcast({"type": "recovery", "payload": result})
    return result


class ReanalyzeRequest(BaseModel):
    anomaly_type: str | None = None
    affected_service: str | None = None


@app.post("/api/incidents/reanalyze")
async def reanalyze(req: ReanalyzeRequest | None = None):
    global _pipeline_state
    anomaly = (req.anomaly_type if req and req.anomaly_type else
               _incident_window.get("anomaly_type", "5xx_spike"))
    affected = (req.affected_service if req and req.affected_service else
                _incident_window.get("affected_service", "payment-service"))
    if anomaly == "none":
        anomaly = "5xx_spike"
        affected = "payment-service"
    state = await run_pipeline(
        anomaly, affected, dict(_services),
        _incident_window["failed_requests"],
        _incident_window["failed_checkouts"],
    )
    _pipeline_state = state
    return {"status": "ok", "incident_id": state.get("incident_id")}


@app.post("/api/reset")
async def reset_all():
    global _pipeline_state, _incident_window, _anomaly_cooldown
    result = await execute_action("full_reset")
    await execute_action("release_load")
    for svc in _services.values():
        svc.update({
            "status": "healthy", "error_rate": 0, "avg_latency_ms": 0,
            "p95_latency_ms": 0, "total_requests": 0, "error_count": 0,
            "status_codes": {}, "logs": [],
        })
        svc["history"] = deque(maxlen=60)
    _pipeline_state = None
    _incident_window = {"active": False, "started_at": 0, "failed_requests": 0,
                        "failed_checkouts": 0, "anomaly_type": "none", "affected_service": ""}
    _anomaly_cooldown = 0
    await broadcast({"type": "reset", "payload": {"status": "ok"}})
    return {"status": "ok", "shop_reset": result}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    _ws_clients.append(ws)
    try:
        await ws.send_json({"type": "telemetry", "payload": _snapshot()})
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    finally:
        if ws in _ws_clients:
            _ws_clients.remove(ws)
