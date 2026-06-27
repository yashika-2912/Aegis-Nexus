"""Product Service — catalog with toggleable route bug."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared import demo_controls
from shared.telemetry_hooks import TelemetryMiddleware, init_service, log_line

init_service("product-service")

app = FastAPI(title="Product Service")
app.add_middleware(TelemetryMiddleware, service_name="product-service")

PRODUCTS = [
    {"id": "prod-1", "name": "Aegis Shield Pro", "price": 149.99, "description": "Enterprise-grade security appliance", "image": "/products/shield.png"},
    {"id": "prod-2", "name": "Nexus Monitor Hub", "price": 299.99, "description": "Real-time observability dashboard", "image": "/products/monitor.png"},
    {"id": "prod-3", "name": "Sentinel AI Node", "price": 499.99, "description": "Autonomous threat detection unit", "image": "/products/sentinel.png"},
    {"id": "prod-4", "name": "Healer Recovery Kit", "price": 79.99, "description": "Self-healing infrastructure toolkit", "image": "/products/healer.png"},
    {"id": "prod-5", "name": "Oracle Predict Engine", "price": 899.99, "description": "Predictive failure analysis module", "image": "/products/oracle.png"},
    {"id": "prod-6", "name": "Sherlock Debug Lens", "price": 199.99, "description": "Root cause analysis instrument", "image": "/products/sherlock.png"},
]


class RouteToggleRequest(BaseModel):
    enabled: bool | None = None


@app.get("/products")
async def list_products():
    if not demo_controls.products_route_enabled:
        log_line("GET /products — route deregistered (404)", "ERROR")
        raise HTTPException(status_code=404, detail="Route /products not found — deployment v1.4 removed this endpoint")
    log_line(f"Serving {len(PRODUCTS)} products")
    return {"products": PRODUCTS}


@app.get("/products/{product_id}")
async def get_product(product_id: str):
    if not demo_controls.products_route_enabled:
        log_line(f"GET /products/{product_id} — route deregistered (404)", "ERROR")
        raise HTTPException(status_code=404, detail="Route not found")
    for p in PRODUCTS:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/demo/toggle-route")
async def toggle_route(req: RouteToggleRequest | None = None):
    if req and req.enabled is not None:
        demo_controls.products_route_enabled = req.enabled
    else:
        demo_controls.products_route_enabled = not demo_controls.products_route_enabled
    state = "enabled" if demo_controls.products_route_enabled else "disabled"
    log_line(f"Product route toggled — now {state}", "WARN")
    return {"products_route_enabled": demo_controls.products_route_enabled}


@app.post("/reset")
async def reset():
    demo_controls.products_route_enabled = True
    log_line("Product service reset — route restored")
    return {"status": "ok", "products_route_enabled": True}


@app.get("/health")
async def health():
    return {
        "status": "healthy" if demo_controls.products_route_enabled else "degraded",
        "service": "product-service",
        "route_enabled": demo_controls.products_route_enabled,
    }
