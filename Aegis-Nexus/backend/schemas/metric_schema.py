from pydantic import BaseModel


class MetricSchema(BaseModel):
    service_id: str
    timestamp: str
    cpu: float
    memory: float
    request_count: int
    request_rate: float
    error_rate: float
    latency: float
    status: str
    available: bool


class MetricsResponse(BaseModel):
    latest: list[MetricSchema]
    history: dict[str, list[MetricSchema]]
