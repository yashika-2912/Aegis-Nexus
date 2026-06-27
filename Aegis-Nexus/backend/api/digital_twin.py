from fastapi import APIRouter, HTTPException

from backend.schemas.digital_twin_schema import (
    FailureEventRequest,
    FailureSimulationRequest,
    ImpactAnalysisResponse,
    TwinGraphSchema,
    TwinServiceNodeSchema,
)
from backend.services.digital_twin_service import digital_twin_service

router = APIRouter(prefix="/digital-twin", tags=["enterprise-digital-twin"])


@router.get("/services", response_model=list[TwinServiceNodeSchema])
async def list_twin_services() -> list[TwinServiceNodeSchema]:
    return digital_twin_service.services()


@router.get("/graph", response_model=TwinGraphSchema)
async def get_graph() -> TwinGraphSchema:
    return digital_twin_service.graph()


@router.post("/events/failure", response_model=ImpactAnalysisResponse)
async def failure_event(payload: FailureEventRequest) -> ImpactAnalysisResponse:
    try:
        return digital_twin_service.failure(payload.service_id, payload.status)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown service") from exc


@router.post("/simulate/failure", response_model=ImpactAnalysisResponse)
async def simulate_failure(payload: FailureSimulationRequest) -> ImpactAnalysisResponse:
    try:
        return digital_twin_service.failure(payload.service_id, "DOWN")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown service") from exc


@router.post("/reset", response_model=TwinGraphSchema)
async def reset_graph() -> TwinGraphSchema:
    return digital_twin_service.reset()


compat_router = APIRouter(tags=["enterprise-digital-twin-compat"])


@compat_router.get("/graph", response_model=TwinGraphSchema)
async def get_graph_compat() -> TwinGraphSchema:
    return await get_graph()


@compat_router.post("/events/failure", response_model=ImpactAnalysisResponse)
async def failure_event_compat(payload: FailureEventRequest) -> ImpactAnalysisResponse:
    return await failure_event(payload)


@compat_router.post("/simulate/failure", response_model=ImpactAnalysisResponse)
async def simulate_failure_compat(payload: FailureSimulationRequest) -> ImpactAnalysisResponse:
    return await simulate_failure(payload)


@compat_router.post("/reset", response_model=TwinGraphSchema)
async def reset_graph_compat() -> TwinGraphSchema:
    return await reset_graph()
