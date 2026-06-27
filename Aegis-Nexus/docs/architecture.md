# Aegis Nexus Phase 1 Architecture

Phase 1 implements the observability foundation only.

```text
Sample Microservices
       |
       v
OpenTelemetry-instrumented Telemetry Service
       |
       v
In-Memory Metrics Store
       |
       +-- REST APIs
       |
       +-- WebSocket Broadcast
              |
              v
        Next.js Dashboard
```

The simulator represents Frontend, Payment, Order, User, and PostgreSQL services. It continuously exports CPU, memory, request count, request rate, error rate, latency, availability, and health status.

Out of scope for Phase 1: AI agents, Neo4j, Kafka, root cause analysis, and autonomous remediation.

## Phase 2 Enterprise Digital Twin

```text
Phase 1 Events
      |
      v
Failure Event API
      |
      v
Digital Twin Graph Store
      |
      +-- Neo4j-compatible service layer
      +-- Impact traversal
      +-- Blast-radius calculation
      +-- Critical-path generation
      |
      v
React Flow Dependency Graph
```

Phase 2 is scoped to dependency modeling and impact analysis. It does not collect telemetry and does not run AI agents.
