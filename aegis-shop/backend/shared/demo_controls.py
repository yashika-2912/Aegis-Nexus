"""Demo control state shared across services (imported by relevant services)."""
from __future__ import annotations

# Product route toggle — simulates bad deployment removing /products
products_route_enabled: bool = True

# Order service memory leak threshold
MEMORY_LEAK_THRESHOLD: int = 50
