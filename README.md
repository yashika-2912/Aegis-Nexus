# Aegis Nexus + Aegis Shop

Two connected applications for autonomous incident response demo:

- **Aegis Shop** — real e-commerce app with intentionally fragile microservices
- **Aegis Nexus** — AI-powered SRE command center that detects, reasons about, fixes, and learns from real failures

> Everything that breaks is a real bug in the backend. Everything that fixes it is a real action Aegis Nexus takes against the services — nothing is a scripted animation.

## Architecture

```
[Aegis Shop user] → Buy Now / load products
        ↓
[API Gateway :8000] → [User :8001 | Product :8002 | Order :8003 | Payment :8004]
        ↓ real errors (404 / 500 / latency)
[Telemetry hooks] → [Aegis Nexus :8010]
        ↓
[Sentinel → Sherlock → Oracle → Healer]  (LangGraph pipeline)
        ↓
[Real remediation] → [Verification] → [Learning panel]
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- (Optional) `GROQ_API_KEY` or `GOOGLE_API_KEY` for LLM agent reasoning — canned fallbacks work without keys

### 1. Install dependencies

```bash
# Shop backend
cd aegis-shop/backend
pip install -r requirements.txt

# Nexus backend
cd ../../aegis-nexus/backend
pip install -r requirements.txt

# Shop frontend
cd ../../aegis-shop/frontend
npm install

# Nexus frontend
cd ../../aegis-nexus/frontend
npm install
```

### 2. Start everything (Windows)

```bash
start-all.bat
```

### 2. Start manually

**Terminal 1 — Shop backend (all 5 services):**
```bash
cd aegis-shop/backend
python run_all.py
```

**Terminal 2 — Nexus backend:**
```bash
cd aegis-nexus/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8010
```

**Terminal 3 — Shop frontend:**
```bash
cd aegis-shop/frontend
npm run dev
```

**Terminal 4 — Nexus frontend:**
```bash
cd aegis-nexus/frontend
npm run dev
```

### URLs

| App | URL |
|-----|-----|
| Aegis Shop | http://localhost:3000 |
| Aegis Nexus | http://localhost:3001 |
| Shop API Gateway | http://localhost:8000 |
| Nexus API | http://localhost:8010 |

**Shop login:** `demo@aegis.shop` / `demo123`

## Demo Script

1. Open **Aegis Shop** — browse products, login, add to cart
2. Expand "Ops Tools" → click **Simulate Traffic Burst** (exhausts payment DB pool)
3. Click **Buy Now** → real HTTP 500 from connection pool exhaustion
4. Switch to **Aegis Nexus** — watch Sentinel detect the spike, Sherlock identify pool exhaustion, Oracle predict cascade, Healer recommend reset
5. Click **Execute Healer Action** — see real before/after verification
6. Return to Shop → **Buy Now** succeeds
7. Check Learning panel for the logged incident with real recovery time

### Other failure modes

| Scenario | Trigger (in Shop Ops Tools) | Symptom |
|----------|----------------------------|---------|
| 404 spike | Toggle Deployment Config | Product page 404s |
| Pool exhaustion | Simulate Traffic Burst + Buy Now | Payment 500 |
| Memory leak | Place 50+ orders via Buy Now | Order latency degrades |

## Reset between demos

Click **Reset All** in Nexus, or:
```bash
curl -X POST http://localhost:8010/api/reset
```

## LLM Configuration

Set one of these environment variables before starting Nexus:

```bash
export GROQ_API_KEY=your_key        # Uses Llama 3.3 70B
export GOOGLE_API_KEY=your_key      # Uses Gemini 2.0 Flash
```

Without keys, agents use scenario-specific canned responses keyed to the detected anomaly type.

## Project Structure

```
aegis-shop/backend/     — Gateway + 4 microservices + payment DB
aegis-shop/frontend/    — Consumer e-commerce UI
aegis-nexus/backend/    — WebSocket hub, agents, remediation, SQLite
aegis-nexus/frontend/   — Dark command-center dashboard
```

## Team

Confluence 2.0 Hackathon — Team Codezilla, Track: AI Automation
