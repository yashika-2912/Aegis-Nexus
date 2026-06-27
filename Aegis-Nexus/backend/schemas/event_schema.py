from pydantic import BaseModel


class EventSchema(BaseModel):
    id: str
    service_id: str
    service_name: str
    type: str
    severity: str
    message: str
    timestamp: str
