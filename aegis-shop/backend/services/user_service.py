"""User Service — mock auth and sessions."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared.telemetry_hooks import TelemetryMiddleware, init_service, log_line

init_service("user-service")

app = FastAPI(title="User Service")
app.add_middleware(TelemetryMiddleware, service_name="user-service")

# Fake users
USERS = {
    "demo@aegis.shop": {"password": "demo123", "name": "Demo User", "id": "user-1"},
    "admin@aegis.shop": {"password": "admin123", "name": "Admin", "id": "user-2"},
}

SESSIONS: dict[str, dict] = {}


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    name: str
    email: str


@app.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    user = USERS.get(req.email)
    if not user or user["password"] != req.password:
        log_line(f"Failed login attempt for {req.email}", "WARN")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = f"tok-{user['id']}-{len(SESSIONS)}"
    SESSIONS[token] = {"email": req.email, "name": user["name"], "id": user["id"]}
    log_line(f"User {req.email} logged in successfully")
    return LoginResponse(token=token, name=user["name"], email=req.email)


@app.get("/session/{token}")
async def validate_session(token: str):
    session = SESSIONS.get(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    return session


@app.post("/reset")
async def reset():
    SESSIONS.clear()
    log_line("User service reset — sessions cleared")
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "user-service", "active_sessions": len(SESSIONS)}
