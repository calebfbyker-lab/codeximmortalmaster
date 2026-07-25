# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import networkx as nx

from .node_factory import node_from_jsonld
from .schema import BaseNode, Edge, EdgeType

try:
    from neo4j import GraphDatabase
except Exception:
    GraphDatabase = None


@dataclass
class GraphQuery:
    node_type: Optional[str] = None
    classification: Optional[str] = None
    tags_any: Optional[list[str]] = None
    limit: int = 50


class MemoryGraphStore:
    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
    ) -> None:
        self.graph = nx.DiGraph()
        self.driver = None
        if neo4j_uri and neo4j_user and neo4j_password:
            if GraphDatabase is None:
                raise RuntimeError("neo4j driver is not installed")
            self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    def close(self) -> None:
        if self.driver:
            self.driver.close()

    def add_node(self, node: BaseNode) -> str:
        self.graph.add_node(node.id, **node.model_dump())
        if self.driver:
            self._neo4j_upsert_node(node)
        return node.id

    def add_edge(self, from_id: str, to_id: str, relation_type: EdgeType | str, metadata: Optional[dict] = None) -> None:
        if from_id not in self.graph or to_id not in self.graph:
            raise KeyError("Both nodes must exist before adding an edge")
        relation = relation_type.value if isinstance(relation_type, EdgeType) else relation_type
        self.graph.add_edge(from_id, to_id, relation_type=relation, metadata=metadata or {})
        if self.driver:
            self._neo4j_upsert_edge(from_id, to_id, relation, metadata or {})

    def query(self, cypher_like_dict: Dict[str, Any]) -> List[BaseNode]:
        spec = GraphQuery(**cypher_like_dict)
        results: List[BaseNode] = []
        for _, attrs in self.graph.nodes(data=True):
            if spec.node_type and attrs.get("node_type") != spec.node_type:
                continue
            if spec.classification and attrs.get("classification") != spec.classification:
                continue
            if spec.tags_any:
                node_tags = set(attrs.get("tags", []))
                if not node_tags.intersection(spec.tags_any):
                    continue
            results.append(node_from_jsonld(self._attrs_to_jsonld(attrs)))
            if len(results) >= spec.limit:
                break
        return results

    def export_jsonld(self) -> dict:
        nodes = [self._attrs_to_jsonld(attrs) for _, attrs in self.graph.nodes(data=True)]
        edges = []
        for source, target, attrs in self.graph.edges(data=True):
            edge = Edge(
                source=source,
                target=target,
                edge_type=EdgeType(attrs["relation_type"]),
                metadata=attrs.get("metadata", {}),
            )
            edges.append(edge.to_jsonld())
        return {
            "@context": {
                "id": "@id",
                "type": "@type",
                "edgeType": "ci:edgeType",
            },
            "@graph": nodes + edges,
        }

    def import_jsonld(self, data: dict) -> None:
        self.graph.clear()
        pending_edges: List[dict] = []
        for item in data.get("@graph", []):
            if item.get("@type") == "Edge":
                pending_edges.append(item)
            else:
                node = node_from_jsonld(item)
                self.add_node(node)
        for item in pending_edges:
            self.add_edge(
                item["source"],
                item["target"],
                item["edgeType"],
                {k: v for k, v in item.items() if k not in {"@id", "@type", "source", "target", "edgeType"}},
            )

    def _attrs_to_jsonld(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        data = dict(attrs)
        data["@id"] = data.pop("id")
        data["@type"] = data.pop("node_type")
        return data

    def _neo4j_upsert_node(self, node: BaseNode) -> None:
        query = """
        MERGE (n:CodexNode {id: $id})
        SET n += $props
        """
        props = node.model_dump()
        with self.driver.session() as session:
            session.run(query, id=node.id, props=props)

    def _neo4j_upsert_edge(self, from_id: str, to_id: str, relation_type: str, metadata: dict) -> None:
        query = f"""
        MATCH (a:CodexNode {{id: $from_id}})
        MATCH (b:CodexNode {{id: $to_id}})
        MERGE (a)-[r:{relation_type}]->(b)
        SET r.metadata = $metadata
        """
        with self.driver.session() as session:
            session.run(query, from_id=from_id, to_id=to_id, metadata=metadata)