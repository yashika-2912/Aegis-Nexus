"""Real telemetry hooks — push metrics and log lines to Aegis Nexus."""
from __future__ import annotations

import asyncio
import json
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

import httpx

NEXUS_TELEMETRY_URL = "http://localhost:8010/api/telemetry/ingest"
SERVICE_NAME = "unknown"

# Ring buffer: last 50 log lines per service (in-process)
_log_buffers: dict[str, deque] = {}


def init_service(name: str) -> None:
    global SERVICE_NAME
    SERVICE_NAME = name
    if name not in _log_buffers:
        _log_buffers[name] = deque(maxlen=50)


def get_log_buffer(service: str | None = None) -> list[str]:
    name = service or SERVICE_NAME
    return list(_log_buffers.get(name, []))


@dataclass
class RequestMetrics:
    total: int = 0
    errors: int = 0
    latencies: deque = field(default_factory=lambda: deque(maxlen=100))
    status_codes: dict[int, int] = field(default_factory=dict)

    def record(self, status: int, latency_ms: float) -> None:
        self.total += 1
        if status >= 400:
            self.errors += 1
        self.latencies.append(latency_ms)
        self.status_codes[status] = self.status_codes.get(status, 0) + 1

    def snapshot(self) -> dict[str, Any]:
        lats = list(self.latencies)
        avg = sum(lats) / len(lats) if lats else 0.0
        p95 = sorted(lats)[int(len(lats) * 0.95)] if lats else 0.0
        error_rate = (self.errors / self.total * 100) if self.total else 0.0
        return {
            "total_requests": self.total,
            "error_count": self.errors,
            "error_rate": round(error_rate, 2),
            "avg_latency_ms": round(avg, 2),
            "p95_latency_ms": round(p95, 2),
            "status_codes": dict(self.status_codes),
        }


_metrics: dict[str, RequestMetrics] = {}


def get_metrics(service: str | None = None) -> RequestMetrics:
    name = service or SERVICE_NAME
    if name not in _metrics:
        _metrics[name] = RequestMetrics()
    return _metrics[name]


def log_line(message: str, level: str = "INFO") -> None:
    entry = f"[{time.strftime('%H:%M:%S')}] [{level}] {message}"
    buf = _log_buffers.setdefault(SERVICE_NAME, deque(maxlen=50))
    buf.append(entry)
    _push_async({"type": "log", "service": SERVICE_NAME, "line": entry, "level": level})


def emit_metric(status: int, latency_ms: float) -> None:
    m = get_metrics()
    m.record(status, latency_ms)
    snap = m.snapshot()
    _push_async({
        "type": "metric",
        "service": SERVICE_NAME,
        "status": status,
        "latency_ms": latency_ms,
        "metrics": snap,
        "timestamp": time.time(),
    })


def _push_async(payload: dict) -> None:
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_send(payload))
    except RuntimeError:
        pass


async def _send(payload: dict) -> None:
    try:
        async with httpx.AsyncClient(timeout=1.0) as client:
            await client.post(NEXUS_TELEMETRY_URL, json=payload)
    except Exception:
        pass


class TelemetryMiddleware:
    """ASGI middleware to record request metrics."""

    def __init__(self, app, service_name: str):
        self.app = app
        init_service(service_name)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            log_line(f"Unhandled exception: {exc}", "ERROR")
            raise
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            emit_metric(status_code, elapsed)
