from fastapi import APIRouter, Depends

from backend.app.dependencies import get_store
from backend.schemas.service_schema import ServiceSchema
from backend.services.metrics_service import serialize_service
from backend.storage.in_memory_store import InMemoryTelemetryStore

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceSchema])
async def list_services(store: InMemoryTelemetryStore = Depends(get_store)) -> list[ServiceSchema]:
    return [serialize_service(service) for service in store.services()]
