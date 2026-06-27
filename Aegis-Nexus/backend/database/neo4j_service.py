from collections.abc import Iterable
from contextlib import suppress

from neo4j import GraphDatabase

from backend.models.digital_twin import TwinDependencyEdge, TwinServiceNode


class Neo4jService:
    def __init__(self, uri: str | None, username: str | None, password: str | None) -> None:
        self._driver = None
        if uri and username and password:
            self._driver = GraphDatabase.driver(uri, auth=(username, password))

    @property
    def enabled(self) -> bool:
        return self._driver is not None

    def close(self) -> None:
        if self._driver:
            self._driver.close()

    def seed_graph(self, nodes: Iterable[TwinServiceNode], edges: Iterable[TwinDependencyEdge]) -> None:
        if not self._driver:
            return
        with suppress(Exception):
            with self._driver.session() as session:
                session.run("MATCH (n:Service) DETACH DELETE n")
                for node in nodes:
                    session.run(
                        """
                        MERGE (s:Service {id: $id})
                        SET s.name = $name,
                            s.type = $type,
                            s.status = $status,
                            s.health = $health,
                            s.last_updated = $last_updated
                        """,
                        id=node.id,
                        name=node.name,
                        type=node.type,
                        status=node.status,
                        health=node.health,
                        last_updated=node.last_updated.isoformat(),
                    )
                for edge in edges:
                    session.run(
                        """
                        MATCH (source:Service {id: $source})
                        MATCH (target:Service {id: $target})
                        MERGE (source)-[:DEPENDS_ON {id: $id}]->(target)
                        """,
                        id=edge.id,
                        source=edge.source,
                        target=edge.target,
                    )

    def update_status(self, node: TwinServiceNode) -> None:
        if not self._driver:
            return
        with suppress(Exception):
            with self._driver.session() as session:
                session.run(
                    """
                    MATCH (s:Service {id: $id})
                    SET s.status = $status,
                        s.health = $health,
                        s.last_updated = $last_updated
                    """,
                    id=node.id,
                    status=node.status,
                    health=node.health,
                    last_updated=node.last_updated.isoformat(),
                )
