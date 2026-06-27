# Aegis Nexus Phase 1 API

## REST

- `GET /services` returns registered demo services and dependency metadata.
- `GET /metrics` returns latest metrics and recent history.
- `GET /metrics?service_id=payment-service` returns history for one service.
- `GET /health` returns global system health KPIs and recent events.

## WebSocket

- `ws://localhost:8000/ws` pushes a `telemetry.update` payload every second.

## Demo Controls

- `POST /simulate/payment-service/down` forces a service unavailable event.
- `POST /simulate/payment-service/recover` restores telemetry generation.

## Phase 2 Enterprise Digital Twin

- `GET /digital-twin/services` returns digital twin service nodes.
- `GET /digital-twin/graph` returns React Flow-compatible graph data.
- `POST /digital-twin/events/failure` consumes a Phase 1 failure event.
- `POST /digital-twin/simulate/failure` runs a demo failure simulation.
- `POST /digital-twin/reset` restores every twin node to Healthy / 100.

Compatibility routes are also exposed for the non-conflicting brief endpoints:

- `GET /graph`
- `POST /events/failure`
- `POST /simulate/failure`
- `POST /reset`
