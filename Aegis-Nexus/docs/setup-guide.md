# Setup Guide

## Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --app-dir . --reload --host 0.0.0.0 --port 8000
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

Open `http://localhost:3000/digital-twin` for the Enterprise Digital Twin.

## Trigger a Demo Incident

```bash
curl -X POST http://localhost:8000/simulate/payment-service/down
curl -X POST http://localhost:8000/simulate/payment-service/recover
```

## Trigger a Digital Twin Failure

```bash
curl -X POST http://localhost:8000/digital-twin/simulate/failure -H "Content-Type: application/json" -d "{\"service_id\":\"payment-db\"}"
curl -X POST http://localhost:8000/digital-twin/reset
```
