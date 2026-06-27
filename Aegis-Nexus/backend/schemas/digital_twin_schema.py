from pydantic import BaseModel, Field


class TwinServiceNodeSchema(BaseModel):
    id: str
    name: str
    type: str
    status: str
    health: int
    last_updated: str


class TwinDependencyEdgeSchema(BaseModel):
    id: str
    source: str
    target: str
    relationship: str = "DEPENDS_ON"


class TwinGraphSchema(BaseModel):
    nodes: list[TwinServiceNodeSchema]
    edges: list[TwinDependencyEdgeSchema]


class FailureEventRequest(BaseModel):
    service_id: str
    status: str = Field(default="DOWN")


class FailureSimulationRequest(BaseModel):
    service_id: str


class ImpactAnalysisResponse(BaseModel):
    failure_origin: str
    affected_services: list[str]
    blast_radius: int
    critical_path: list[str]
    suggested_root_cause: str
    graph: TwinGraphSchema
