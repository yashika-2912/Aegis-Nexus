# Aegis Nexus

Phase 1 and Phase 2 implementation for Aegis Nexus.

Phase 1 monitors a running demo microservices application, ingests telemetry, evaluates health thresholds, and streams updates to a professional DevOps dashboard.

Phase 2 adds the Enterprise Digital Twin: dependency graph storage, failure propagation, blast-radius analysis, and graph APIs for future AI agents.

## Services Monitored

- Frontend Service
- Payment Service
- Order Service
- User Service
- PostgreSQL Database

## Telemetry

- CPU usage
- Memory usage
- Request count
- Request throughput
- Error rate
- Response latency
- Service status

## Run Locally

```bash
pip install -r requirements.txt
uvicorn backend.app.main:app --app-dir . --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Dashboard: `http://localhost:3000`
Backend API: `http://localhost:8000`
Digital Twin: `http://localhost:3000/digital-twin`

## Demo Incident

```bash
curl -X POST http://localhost:8000/simulate/payment-service/down
curl -X POST http://localhost:8000/simulate/payment-service/recover
```

## Phase 2 Digital Twin APIs

```bash
curl http://localhost:8000/digital-twin/graph
curl -X POST http://localhost:8000/digital-twin/simulate/failure -H "Content-Type: application/json" -d "{\"service_id\":\"payment-db\"}"
curl -X POST http://localhost:8000/digital-twin/reset
```

## Scope

Phase 2 intentionally does not include AI agents, telemetry collection, root cause analysis, or autonomous remediation.
