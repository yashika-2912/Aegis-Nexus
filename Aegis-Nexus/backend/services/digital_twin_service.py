from backend.app.config import settings
from backend.database.neo4j_service import Neo4jService
from backend.graph.digital_twin_store import DigitalTwinStore
from backend.graph.seed import SEED_EDGES, SEED_NODES
from backend.models.digital_twin import ImpactAnalysis, TwinDependencyEdge, TwinServiceNode
from backend.schemas.digital_twin_schema import (
    ImpactAnalysisResponse,
    TwinDependencyEdgeSchema,
    TwinGraphSchema,
    TwinServiceNodeSchema,
)
from backend.utils.timestamps import isoformat


class DigitalTwinService:
    def __init__(self) -> None:
        self.store = DigitalTwinStore(SEED_NODES, SEED_EDGES)
        self.neo4j = Neo4jService(settings.neo4j_uri, settings.neo4j_username, settings.neo4j_password)
        self.neo4j.seed_graph(self.store.nodes(), self.store.edges())

    def services(self) -> list[TwinServiceNodeSchema]:
        return [self._serialize_node(node) for node in self.store.nodes()]

    def graph(self) -> TwinGraphSchema:
        nodes, edges = self.store.graph()
        return TwinGraphSchema(
            nodes=[self._serialize_node(node) for node in nodes],
            edges=[self._serialize_edge(edge) for edge in edges],
        )

    def failure(self, service_id: str, status: str = "DOWN") -> ImpactAnalysisResponse:
        analysis = self.store.apply_failure(service_id, status="Down" if status.upper() == "DOWN" else "Critical")
        for node in self.store.nodes():
            self.neo4j.update_status(node)
        return self._impact_response(analysis)

    def reset(self) -> TwinGraphSchema:
        self.store.reset()
        for node in self.store.nodes():
            self.neo4j.update_status(node)
        return self.graph()

    def _impact_response(self, analysis: ImpactAnalysis) -> ImpactAnalysisResponse:
        return ImpactAnalysisResponse(
            failure_origin=analysis.failure_origin,
            affected_services=analysis.affected_services,
            blast_radius=analysis.blast_radius,
            critical_path=analysis.critical_path,
            suggested_root_cause=analysis.suggested_root_cause,
            graph=self.graph(),
        )

    @staticmethod
    def _serialize_node(node: TwinServiceNode) -> TwinServiceNodeSchema:
        return TwinServiceNodeSchema(
            id=node.id,
            name=node.name,
            type=node.type,
            status=node.status,
            health=node.health,
            last_updated=isoformat(node.last_updated),
        )

    @staticmethod
    def _serialize_edge(edge: TwinDependencyEdge) -> TwinDependencyEdgeSchema:
        return TwinDependencyEdgeSchema(
            id=edge.id,
            source=edge.source,
            target=edge.target,
            relationship=edge.relationship,
        )


digital_twin_service = DigitalTwinService()
