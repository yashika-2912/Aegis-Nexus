from backend.models.digital_twin import TwinDependencyEdge, TwinServiceNode

SEED_NODES = [
    TwinServiceNode("api-gateway", "API Gateway", "Gateway"),
    TwinServiceNode("user-service", "User Service", "Microservice"),
    TwinServiceNode("order-service", "Order Service", "Microservice"),
    TwinServiceNode("payment-service", "Payment Service", "Microservice"),
    TwinServiceNode("payment-db", "Payment Database", "Database"),
    TwinServiceNode("order-db", "Order Database", "Database"),
    TwinServiceNode("redis-cache", "Redis Cache", "Cache"),
    TwinServiceNode("event-queue", "Event Queue", "Queue"),
]

SEED_EDGES = [
    TwinDependencyEdge("api-gateway-user-service", "api-gateway", "user-service"),
    TwinDependencyEdge("api-gateway-order-service", "api-gateway", "order-service"),
    TwinDependencyEdge("api-gateway-payment-service", "api-gateway", "payment-service"),
    TwinDependencyEdge("order-service-payment-service", "order-service", "payment-service"),
    TwinDependencyEdge("order-service-order-db", "order-service", "order-db"),
    TwinDependencyEdge("order-service-event-queue", "order-service", "event-queue"),
    TwinDependencyEdge("payment-service-payment-db", "payment-service", "payment-db"),
    TwinDependencyEdge("payment-service-redis-cache", "payment-service", "redis-cache"),
    TwinDependencyEdge("user-service-redis-cache", "user-service", "redis-cache"),
]
