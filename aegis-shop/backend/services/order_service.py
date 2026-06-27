"""Order Service — order creation with real memory leak."""
from __future__ import annotations

import asyncio
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared import demo_controls
from shared.telemetry_hooks import TelemetryMiddleware, init_service, log_line

init_service("order-service")

app = FastAPI(title="Order Service")
app.add_middleware(TelemetryMiddleware, service_name="order-service")

# REAL memory leak — never cleared until reset
_leaked_orders: list[dict] = []
_orders: dict[str, dict] = {}


class CreateOrderRequest(BaseModel):
    product_id: str
    product_name: str
    quantity: int = 1
    price: float
    user_email: str


class OrderResponse(BaseModel):
    order_id: str
    status: str
    total: float


def _leak_size() -> int:
    return len(_leaked_orders)


def _simulate_leak_work() -> None:
    """Past threshold, each request does O(n) work — real latency degradation."""
    n = len(_leaked_orders)
    if n > demo_controls.MEMORY_LEAK_THRESHOLD:
        # Real CPU work proportional to leak size
        total = 0
        for item in _leaked_orders:
            total += hash(str(item))
        _ = total


@app.post("/orders", response_model=OrderResponse)
async def create_order(req: CreateOrderRequest):
    _simulate_leak_work()

    order_id = f"ord-{uuid.uuid4().hex[:8]}"
    total = req.price * req.quantity
    order = {
        "order_id": order_id,
        "product_id": req.product_id,
        "product_name": req.product_name,
        "quantity": req.quantity,
        "price": req.price,
        "total": total,
        "user_email": req.user_email,
        "status": "pending",
        "created_at": time.time(),
    }
    _orders[order_id] = order

    # Intentional leak — append copy and never remove
    leak_entry = {**order, "leak_metadata": list(range(100))}
    _leaked_orders.append(leak_entry)

    leak_size = _leak_size()
    if leak_size > demo_controls.MEMORY_LEAK_THRESHOLD:
        log_line(
            f"Memory leak threshold exceeded ({leak_size} entries) — latency degrading",
            "WARN",
        )
        # Add real delay proportional to leak
        await asyncio.sleep(min(leak_size * 0.002, 2.0))

    log_line(f"Order {order_id} created for {req.user_email} (leak size: {leak_size})")
    return OrderResponse(order_id=order_id, status="pending", total=total)


@app.get("/orders")
async def list_orders():
    _simulate_leak_work()
    leak_size = _leak_size()
    if leak_size > demo_controls.MEMORY_LEAK_THRESHOLD:
        await asyncio.sleep(min(leak_size * 0.001, 1.0))
    return {"orders": list(_orders.values()), "leak_size": leak_size}


@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    _simulate_leak_work()
    order = _orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post("/reset")
async def reset():
    global _leaked_orders, _orders
    _leaked_orders.clear()
    _orders.clear()
    log_line("Order service reset — leak cleared")
    return {"status": "ok", "leak_size": 0}


@app.get("/health")
async def health():
    leak_size = _leak_size()
    status = "healthy"
    if leak_size > demo_controls.MEMORY_LEAK_THRESHOLD:
        status = "degraded"
    elif leak_size > demo_controls.MEMORY_LEAK_THRESHOLD * 0.7:
        status = "warning"
    return {
        "status": status,
        "service": "order-service",
        "leak_size": leak_size,
        "threshold": demo_controls.MEMORY_LEAK_THRESHOLD,
    }
