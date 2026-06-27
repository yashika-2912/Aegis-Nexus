"""Pre-seed historical incidents for the learning panel."""
import time

SEED_INCIDENTS = [
    {
        "triggered_at": time.time() - 86400 * 7,
        "resolved_at": time.time() - 86400 * 7 + 4.2,
        "anomaly_type": "5xx_spike",
        "affected_service": "payment-service",
        "root_cause": "Connection pool exhausted on Payment DB after traffic spike",
        "action_taken": "Reset Connection Pool",
        "recovery_time_ms": 4200,
        "outcome": "success",
        "failed_requests": 23,
        "failed_checkouts": 18,
        "severity": "P1",
        "agent_outputs": {"sentinel": "5xx spike detected", "sherlock": "Pool exhaustion", "healer": "Reset pool"},
    },
    {
        "triggered_at": time.time() - 86400 * 5,
        "resolved_at": time.time() - 86400 * 5 + 2.8,
        "anomaly_type": "404_spike",
        "affected_service": "product-service",
        "root_cause": "Route /products deregistered after deployment v1.3",
        "action_taken": "Restore Route",
        "recovery_time_ms": 2800,
        "outcome": "success",
        "failed_requests": 156,
        "failed_checkouts": 0,
        "severity": "P2",
        "agent_outputs": {},
    },
    {
        "triggered_at": time.time() - 86400 * 4,
        "resolved_at": time.time() - 86400 * 4 + 6.1,
        "anomaly_type": "latency_degradation",
        "affected_service": "order-service",
        "root_cause": "Memory leak in order processing — in-memory list exceeded threshold",
        "action_taken": "Clear Leak / Restart Order Service",
        "recovery_time_ms": 6100,
        "outcome": "success",
        "failed_requests": 45,
        "failed_checkouts": 12,
        "severity": "P2",
        "agent_outputs": {},
    },
    {
        "triggered_at": time.time() - 86400 * 3,
        "resolved_at": time.time() - 86400 * 3 + 3.5,
        "anomaly_type": "5xx_spike",
        "affected_service": "payment-service",
        "root_cause": "Connection pool exhausted during flash sale",
        "action_taken": "Reset Connection Pool",
        "recovery_time_ms": 3500,
        "outcome": "success",
        "failed_requests": 67,
        "failed_checkouts": 52,
        "severity": "P1",
        "agent_outputs": {},
    },
    {
        "triggered_at": time.time() - 86400 * 2,
        "resolved_at": time.time() - 86400 * 2 + 8.0,
        "anomaly_type": "latency_degradation",
        "affected_service": "order-service",
        "root_cause": "Unbounded in-memory order cache causing O(n) latency growth",
        "action_taken": "Clear Leak / Restart Order Service",
        "recovery_time_ms": 8000,
        "outcome": "success",
        "failed_requests": 89,
        "failed_checkouts": 34,
        "severity": "P2",
        "agent_outputs": {},
    },
    {
        "triggered_at": time.time() - 86400 * 1.5,
        "resolved_at": time.time() - 86400 * 1.5 + 5.2,
        "anomaly_type": "404_spike",
        "affected_service": "product-service",
        "root_cause": "Bad config rollback removed product catalog endpoint",
        "action_taken": "Restore Route",
        "recovery_time_ms": 5200,
        "outcome": "success",
        "failed_requests": 234,
        "failed_checkouts": 0,
        "severity": "P2",
        "agent_outputs": {},
    },
    {
        "triggered_at": time.time() - 3600 * 12,
        "resolved_at": time.time() - 3600 * 12 + 4.0,
        "anomaly_type": "5xx_spike",
        "affected_service": "payment-service",
        "root_cause": "DB connection pool saturation from concurrent checkout burst",
        "action_taken": "Reset Connection Pool",
        "recovery_time_ms": 4000,
        "outcome": "failed",
        "failed_requests": 12,
        "failed_checkouts": 12,
        "severity": "P1",
        "agent_outputs": {},
    },
    {
        "triggered_at": time.time() - 3600 * 6,
        "resolved_at": time.time() - 3600 * 6 + 2.1,
        "anomaly_type": "404_spike",
        "affected_service": "api-gateway",
        "root_cause": "Upstream product-service route missing — propagated 404",
        "action_taken": "Restore Route",
        "recovery_time_ms": 2100,
        "outcome": "success",
        "failed_requests": 78,
        "failed_checkouts": 0,
        "severity": "P3",
        "agent_outputs": {},
    },
]


def seed_if_empty() -> int:
    from models.db import get_conn, init_db
    init_db()
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
    if count > 0:
        conn.close()
        return 0
    seeded = 0
    for inc in SEED_INCIDENTS:
        import json
        conn.execute(
            """INSERT INTO incidents
               (triggered_at, resolved_at, anomaly_type, affected_service, root_cause,
                action_taken, recovery_time_ms, outcome, failed_requests, failed_checkouts,
                severity, agent_outputs)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                inc["triggered_at"], inc["resolved_at"], inc["anomaly_type"],
                inc["affected_service"], inc["root_cause"], inc["action_taken"],
                inc["recovery_time_ms"], inc["outcome"], inc["failed_requests"],
                inc["failed_checkouts"], inc["severity"],
                json.dumps(inc.get("agent_outputs", {})),
            ),
        )
        seeded += 1
    conn.commit()
    conn.close()
    return seeded
