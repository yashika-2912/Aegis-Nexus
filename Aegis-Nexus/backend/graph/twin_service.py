"""In-memory digital twin for the Nexus API (no Neo4j required)."""
from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock

from graph.twin_seed import SEED_EDGES, SEED_NODES
from models.digital_twin import ImpactAnalysis, TwinDependencyEdge, TwinServiceNode, TwinStatus
from schemas.digital_twin_schema import (
    ImpactAnalysisResponse,
    TwinDependencyEdgeSchema,
    TwinGraphSchema,
    TwinServiceNodeSchema,
)
from utils.timestamps import isoformat


class _TwinStore:
    def __init__(self) -> None:
        self._lock = RLock()
        self._original_nodes = deepcopy(SEED_NODES)
        self._edges = deepcopy(SEED_EDGES)
        self._nodes = {node.id: deepcopy(node) for node in SEED_NODES}
        self._dependents = self._build_dependents(self._edges)

    def graph(self) -> TwinGraphSchema:
        with self._lock:
            return TwinGraphSchema(
                nodes=[self._serialize_node(node) for node in self._nodes.values()],
                edges=[self._serialize_edge(edge) for edge in self._edges],
            )

    def failure(self, service_id: str, status: str = "DOWN") -> ImpactAnalysisResponse:
        with self._lock:
            if service_id not in self._nodes:
                raise KeyError(service_id)

            self._reset_impacted_only()
            origin = self._nodes[service_id]
            origin.status = "Down" if status.upper() == "DOWN" else "Critical"
            origin.health = 0
            origin.last_updated = self._now()

            impacted_ids = self._traverse_dependents(service_id)
            for impacted_id in impacted_ids:
                node = self._nodes[impacted_id]
                if node.status != "Down":
                    node.status = "Affected"
                    node.last_updated = self._now()

            critical_path_ids = self._critical_path(service_id)
            analysis = ImpactAnalysis(
                failure_origin=origin.name,
                affected_services=[self._nodes[node_id].name for node_id in impacted_ids],
                blast_radius=len(impacted_ids) + 1,
                critical_path=[self._nodes[node_id].name for node_id in critical_path_ids],
                suggested_root_cause=f"{origin.name} unavailable.",
            )
            return ImpactAnalysisResponse(
                failure_origin=analysis.failure_origin,
                affected_services=analysis.affected_services,
                blast_radius=analysis.blast_radius,
                critical_path=analysis.critical_path,
                suggested_root_cause=analysis.suggested_root_cause,
                graph=self.graph(),
            )

    def reset(self) -> TwinGraphSchema:
        with self._lock:
            self._nodes = {node.id: deepcopy(node) for node in self._original_nodes}
            current = self._now()
            for node in self._nodes.values():
                node.last_updated = current
            return self.graph()

    def _reset_impacted_only(self) -> None:
        for node in self._nodes.values():
            if node.status in {"Affected", "Down", "Critical"}:
                node.status = "Healthy"
                node.health = 100
                node.last_updated = self._now()

    def _traverse_dependents(self, service_id: str) -> list[str]:
        visited: set[str] = set()
        queue: deque[str] = deque(self._dependents.get(service_id, []))
        ordered: list[str] = []
        while queue:
            node_id = queue.popleft()
            if node_id in visited:
                continue
            visited.add(node_id)
            ordered.append(node_id)
            queue.extend(self._dependents.get(node_id, []))
        return ordered

    def _critical_path(self, service_id: str) -> list[str]:
        best_path: list[str] = [service_id]

        def visit(current_id: str, path: list[str]) -> None:
            nonlocal best_path
            dependents = self._dependents.get(current_id, [])
            if not dependents and len(path) > len(best_path):
                best_path = path[:]
            for dependent_id in dependents:
                visit(dependent_id, [dependent_id, *path])

        visit(service_id, [service_id])
        return best_path

    @staticmethod
    def _build_dependents(edges: list[TwinDependencyEdge]) -> dict[str, list[str]]:
        dependents: dict[str, list[str]] = defaultdict(list)
        for edge in edges:
            dependents[edge.target].append(edge.source)
        return dependents

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

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)


_twin_store = _TwinStore()


def twin_graph() -> TwinGraphSchema:
    return _twin_store.graph()


def twin_simulate_failure(service_id: str) -> ImpactAnalysisResponse:
    return _twin_store.failure(service_id, "DOWN")


def twin_reset() -> TwinGraphSchema:
    return _twin_store.reset()
