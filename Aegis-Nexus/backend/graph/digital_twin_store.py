from collections import defaultdict, deque
from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock

from backend.models.digital_twin import ImpactAnalysis, TwinDependencyEdge, TwinServiceNode, TwinStatus


class DigitalTwinStore:
    def __init__(self, nodes: list[TwinServiceNode], edges: list[TwinDependencyEdge]) -> None:
        self._lock = RLock()
        self._original_nodes = deepcopy(nodes)
        self._edges = deepcopy(edges)
        self._nodes = {node.id: deepcopy(node) for node in nodes}
        self._dependents = self._build_dependents(edges)
        self._dependencies = self._build_dependencies(edges)

    def nodes(self) -> list[TwinServiceNode]:
        with self._lock:
            return list(self._nodes.values())

    def edges(self) -> list[TwinDependencyEdge]:
        with self._lock:
            return list(self._edges)

    def get_node(self, service_id: str) -> TwinServiceNode | None:
        with self._lock:
            return self._nodes.get(service_id)

    def dependencies(self, service_id: str) -> list[TwinServiceNode]:
        with self._lock:
            return [self._nodes[node_id] for node_id in self._dependencies.get(service_id, [])]

    def dependents(self, service_id: str) -> list[TwinServiceNode]:
        with self._lock:
            return [self._nodes[node_id] for node_id in self._dependents.get(service_id, [])]

    def graph(self) -> tuple[list[TwinServiceNode], list[TwinDependencyEdge]]:
        return self.nodes(), self.edges()

    def apply_failure(self, service_id: str, status: TwinStatus = "Down") -> ImpactAnalysis:
        with self._lock:
            if service_id not in self._nodes:
                raise KeyError(service_id)

            self._reset_impacted_only()
            origin = self._nodes[service_id]
            origin.status = "Down" if status.upper() == "DOWN" else status
            origin.health = 0
            origin.last_updated = self._now()

            impacted_ids = self._traverse_dependents(service_id)
            for impacted_id in impacted_ids:
                node = self._nodes[impacted_id]
                if node.status != "Down":
                    node.status = "Affected"
                    node.last_updated = self._now()

            critical_path_ids = self._critical_path(service_id)
            affected_names = [self._nodes[node_id].name for node_id in impacted_ids]
            return ImpactAnalysis(
                failure_origin=origin.name,
                affected_services=affected_names,
                blast_radius=len(impacted_ids) + 1,
                critical_path=[self._nodes[node_id].name for node_id in critical_path_ids],
                suggested_root_cause=f"{origin.name} unavailable.",
            )

    def reset(self) -> None:
        with self._lock:
            self._nodes = {node.id: deepcopy(node) for node in self._original_nodes}
            current = self._now()
            for node in self._nodes.values():
                node.last_updated = current

    def _reset_impacted_only(self) -> None:
        for node in self._nodes.values():
            if node.status in {"Affected", "Down"}:
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
    def _build_dependencies(edges: list[TwinDependencyEdge]) -> dict[str, list[str]]:
        dependencies: dict[str, list[str]] = defaultdict(list)
        for edge in edges:
            dependencies[edge.source].append(edge.target)
        return dependencies

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)
