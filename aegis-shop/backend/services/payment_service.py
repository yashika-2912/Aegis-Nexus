"""Payment Service — processes payments via real connection pool."""
from __future__ import annotations

import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from services.payment_db import (
    ConnectionPoolExhausted,
    get_load_held,
    get_pool,
    release_all_held,
    reset_pool,
)
from shared.telemetry_hooks import TelemetryMiddleware, init_service, log_line

init_service("payment-service")

DB_PATH = str(Path(__file__).resolve().parent.parent / "payment.db")

app = FastAPI(title="Payment Service")
app.add_middleware(TelemetryMiddleware, service_name="payment-service")


class PaymentRequest(BaseModel):
    order_id: str
    amount: float
    user_email: str


class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    order_id: str


class LoadGeneratorRequest(BaseModel):
    connections: int = 3


@app.post("/payments", response_model=PaymentResponse)
def process_payment(req: PaymentRequest):
    pool = get_pool(DB_PATH)
    try:
        with pool.acquire(timeout=1.0) as conn:
            payment_id = f"pay-{uuid.uuid4().hex[:8]}"
            conn.execute(
                "INSERT INTO payments (order_id, amount, status, created_at) VALUES (?, ?, ?, ?)",
                (req.order_id, req.amount, "completed", time.time()),
            )
            conn.commit()
            log_line(f"Payment {payment_id} completed for order {req.order_id} (${req.amount})")
            return PaymentResponse(payment_id=payment_id, status="completed", order_id=req.order_id)
    except ConnectionPoolExhausted as exc:
        log_line(f"Payment failed — {exc}", "ERROR")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/demo/load-generator")
def load_generator(req: LoadGeneratorRequest | None = None):
    """Hold N connections open to genuinely exhaust the pool."""
    n = req.connections if req else 3
    pool = get_pool(DB_PATH)
    held = get_load_held()
    opened = 0
    errors = []
    for _ in range(n):
        try:
            conn = pool.hold_connection()
            held.append(conn)
            opened += 1
        except ConnectionPoolExhausted as exc:
            errors.append(str(exc))
            break
    log_line(f"Load generator opened {opened} held connections (pool max={pool.max_size})", "WARN")
    return {
        "connections_held": len(held),
        "pool_stats": pool.stats(),
        "errors": errors,
    }


@app.post("/demo/release-load")
def release_load():
    released = release_all_held(DB_PATH)
    log_line(f"Released {released} held connections")
    return {"released": released, "pool_stats": get_pool(DB_PATH).stats()}


@app.post("/reset")
def reset():
    reset_pool(DB_PATH)
    log_line("Payment service reset — pool recreated")
    return {"status": "ok", "pool_stats": get_pool(DB_PATH).stats()}


@app.get("/health")
def health():
    pool = get_pool(DB_PATH)
    stats = pool.stats()
    status = "healthy"
    if stats["available"] == 0:
        status = "critical"
    elif stats["available"] <= 1:
        status = "degraded"
    return {"status": status, "service": "payment-service", "pool": stats}


@app.get("/payments")
def list_payments():
    pool = get_pool(DB_PATH)
    with pool.acquire(timeout=1.0) as conn:
        rows = conn.execute("SELECT * FROM payments ORDER BY created_at DESC LIMIT 50").fetchall()
        return {"payments": [dict(r) for r in rows]}
