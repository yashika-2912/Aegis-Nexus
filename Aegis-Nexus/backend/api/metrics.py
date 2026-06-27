from fastapi import APIRouter, Depends, HTTPException

from backend.app.dependencies import get_store
from backend.schemas.metric_schema import MetricsResponse
from backend.services.metrics_service import serialize_metric
from backend.storage.in_memory_store import InMemoryTelemetryStore

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=MetricsResponse)
async def metrics(
    service_id: str | None = None,
    store: InMemoryTelemetryStore = Depends(get_store),
) -> MetricsResponse:
    history = store.history(service_id)
    if service_id and service_id not in history:
        raise HTTPException(status_code=404, detail="Unknown service")
    return MetricsResponse(
        latest=[serialize_metric(metric) for metric in store.latest_metrics()],
        history={key: [serialize_metric(metric) for metric in values] for key, values in history.items()},
    )
