"""SQLite persistence for incident history."""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "nexus.db"


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            triggered_at REAL NOT NULL,
            resolved_at REAL,
            anomaly_type TEXT NOT NULL,
            affected_service TEXT NOT NULL,
            root_cause TEXT,
            action_taken TEXT,
            recovery_time_ms REAL,
            outcome TEXT DEFAULT 'pending',
            failed_requests INTEGER DEFAULT 0,
            failed_checkouts INTEGER DEFAULT 0,
            severity TEXT DEFAULT 'P3',
            agent_outputs TEXT DEFAULT '{}'
        )
    """)
    conn.commit()
    conn.close()


def insert_incident(data: dict) -> int:
    conn = get_conn()
    agent_outputs = json.dumps(data.get("agent_outputs", {}))
    cur = conn.execute(
        """INSERT INTO incidents
           (triggered_at, resolved_at, anomaly_type, affected_service, root_cause,
            action_taken, recovery_time_ms, outcome, failed_requests, failed_checkouts,
            severity, agent_outputs)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data.get("triggered_at", time.time()),
            data.get("resolved_at"),
            data["anomaly_type"],
            data["affected_service"],
            data.get("root_cause", ""),
            data.get("action_taken", ""),
            data.get("recovery_time_ms"),
            data.get("outcome", "pending"),
            data.get("failed_requests", 0),
            data.get("failed_checkouts", 0),
            data.get("severity", "P3"),
            agent_outputs,
        ),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def update_incident(incident_id: int, data: dict) -> None:
    conn = get_conn()
    fields = []
    values = []
    for key in ["resolved_at", "root_cause", "action_taken", "recovery_time_ms", "outcome", "severity"]:
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if "agent_outputs" in data:
        fields.append("agent_outputs = ?")
        values.append(json.dumps(data["agent_outputs"]))
    if fields:
        values.append(incident_id)
        conn.execute(f"UPDATE incidents SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
    conn.close()


def get_incidents(limit: int = 50) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM incidents ORDER BY triggered_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["agent_outputs"] = json.loads(d.get("agent_outputs") or "{}")
        result.append(d)
    return result


def get_learning_stats() -> list[dict]:
    conn = get_conn()
    rows = conn.execute("""
        SELECT action_taken,
               COUNT(*) as total,
               SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as successes,
               AVG(CASE WHEN outcome = 'success' THEN recovery_time_ms ELSE NULL END) as avg_recovery_ms
        FROM incidents
        WHERE action_taken IS NOT NULL AND action_taken != ''
        GROUP BY action_taken
    """).fetchall()
    conn.close()
    stats = []
    for r in rows:
        total = r["total"] or 0
        successes = r["successes"] or 0
        stats.append({
            "action": r["action_taken"],
            "total": total,
            "success_rate": round(successes / total * 100, 1) if total else 0,
            "avg_recovery_ms": round(r["avg_recovery_ms"] or 0, 0),
        })
    return stats
