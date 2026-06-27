from pydantic import BaseModel


class DependencySchema(BaseModel):
    id: str
    name: str
    status: str


class ServiceSchema(BaseModel):
    id: str
    name: str
    kind: str
    description: str
    owner: str
    status: str
    available: bool
    dependencies: list[DependencySchema]
