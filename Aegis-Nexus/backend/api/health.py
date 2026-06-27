from fastapi import APIRouter, Depends

from backend.app.dependencies import get_store
from backend.services.health_service import health_service
from backend.services.metrics_service import serialize_event
from backend.storage.in_memory_store import InMemoryTelemetryStore

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health(store: InMemoryTelemetryStore = Depends(get_store)) -> dict:
    metrics = store.latest_metrics()
    return {
        "status": "ok",
        **health_service.system_health(metrics),
        "events": [serialize_event(event) for event in store.events()[:10]],
    }
