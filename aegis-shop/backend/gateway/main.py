"""API Gateway — routes requests to microservices."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from shared.telemetry_hooks import TelemetryMiddleware, init_service, log_line

init_service("api-gateway")

USER_SERVICE = "http://localhost:8001"
PRODUCT_SERVICE = "http://localhost:8002"
ORDER_SERVICE = "http://localhost:8003"
PAYMENT_SERVICE = "http://localhost:8004"

app = FastAPI(title="Aegis Shop API Gateway")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TelemetryMiddleware, service_name="api-gateway")


class LoginRequest(BaseModel):
    email: str
    password: str


class BuyNowRequest(BaseModel):
    product_id: str
    product_name: str
    price: float
    quantity: int = 1
    user_email: str


async def _proxy(client: httpx.AsyncClient, method: str, url: str, **kwargs) -> httpx.Response:
    start = time.perf_counter()
    try:
        resp = await client.request(method, url, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        log_line(f"{method} {url} → {resp.status_code} ({elapsed:.0f}ms)")
        return resp
    except httpx.RequestError as exc:
        log_line(f"{method} {url} → connection error: {exc}", "ERROR")
        raise HTTPException(status_code=502, detail=f"Service unavailable: {exc}")


@app.get("/")
async def root():
    return {
        "service": "Aegis Shop API Gateway",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "products": "/products",
    }


@app.post("/login")
async def login(req: LoginRequest):
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await _proxy(client, "POST", f"{USER_SERVICE}/login", json=req.model_dump())
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.json())
        return resp.json()


@app.get("/products")
async def products():
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await _proxy(client, "GET", f"{PRODUCT_SERVICE}/products")
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.json().get("detail", resp.text))
        return resp.json()


@app.get("/products/{product_id}")
async def product(product_id: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await _proxy(client, "GET", f"{PRODUCT_SERVICE}/products/{product_id}")
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.json().get("detail", resp.text))
        return resp.json()


@app.post("/checkout/buy-now")
async def buy_now(req: BuyNowRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Create order
        order_resp = await _proxy(
            client, "POST", f"{ORDER_SERVICE}/orders",
            json={
                "product_id": req.product_id,
                "product_name": req.product_name,
                "quantity": req.quantity,
                "price": req.price,
                "user_email": req.user_email,
            },
        )
        if order_resp.status_code >= 400:
            raise HTTPException(status_code=order_resp.status_code, detail=order_resp.json())

        order = order_resp.json()
        total = order["total"]

        # Step 2: Process payment
        pay_resp = await _proxy(
            client, "POST", f"{PAYMENT_SERVICE}/payments",
            json={"order_id": order["order_id"], "amount": total, "user_email": req.user_email},
        )
        if pay_resp.status_code >= 400:
            detail = pay_resp.json().get("detail", pay_resp.text) if pay_resp.headers.get("content-type", "").startswith("application/json") else pay_resp.text
            raise HTTPException(status_code=pay_resp.status_code, detail=detail)

        payment = pay_resp.json()
        log_line(f"Buy Now completed: order={order['order_id']} payment={payment['payment_id']}")
        return {
            "order": order,
            "payment": payment,
            "status": "success",
        }


@app.get("/orders")
async def orders():
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await _proxy(client, "GET", f"{ORDER_SERVICE}/orders")
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()


# Demo controls — live in Shop, not Nexus
@app.post("/demo/toggle-route")
async def toggle_route():
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await _proxy(client, "POST", f"{PRODUCT_SERVICE}/demo/toggle-route")
        return resp.json()


@app.post("/demo/load-generator")
async def load_generator():
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await _proxy(client, "POST", f"{PAYMENT_SERVICE}/demo/load-generator", json={"connections": 3})
        return resp.json()


@app.post("/reset")
async def reset_all():
    async with httpx.AsyncClient(timeout=5.0) as client:
        results = {}
        for name, url in [
            ("product", f"{PRODUCT_SERVICE}/reset"),
            ("order", f"{ORDER_SERVICE}/reset"),
            ("payment", f"{PAYMENT_SERVICE}/reset"),
            ("user", f"{USER_SERVICE}/reset"),
        ]:
            try:
                r = await client.post(url)
                results[name] = r.json() if r.status_code == 200 else r.text
            except Exception as exc:
                results[name] = str(exc)
        log_line("Full shop reset completed")
        return {"status": "ok", "services": results}


@app.get("/health")
async def health():
    services = {}
    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, url in [
            ("user-service", USER_SERVICE),
            ("product-service", PRODUCT_SERVICE),
            ("order-service", ORDER_SERVICE),
            ("payment-service", PAYMENT_SERVICE),
        ]:
            try:
                r = await client.get(f"{url}/health")
                services[name] = r.json()
            except Exception:
                services[name] = {"status": "down"}
    return {"status": "ok", "gateway": "healthy", "services": services}
