# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from typing import Callable, Dict, List, Optional
from .schema import BaseNode, Edge, EdgeType, GraphKind


class KnowledgeStore:
    def __init__(self) -> None:
        self.nodes: Dict[str, BaseNode] = {}
        self.edges: List[Edge] = []

    def upsert_node(self, node: BaseNode) -> None:
        if node.graph != GraphKind.KNOWLEDGE:
            raise ValueError("Node must belong to knowledge graph")
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise KeyError("Both edge endpoints must exist in the knowledge graph")
        self.edges.append(edge)

    def has_node(self, node_id: str) -> bool:
        return node_id in self.nodes

    def get_node(self, node_id: str) -> Optional[BaseNode]:
        return self.nodes.get(node_id)

    def neighbors(self, node_id: str, edge_type: EdgeType | None = None) -> List[BaseNode]:
        result: List[BaseNode] = []
        for edge in self.edges:
            if edge.source == node_id and (edge_type is None or edge.edge_type == edge_type):
                target = self.nodes.get(edge.target)
                if target is not None:
                    result.append(target)
        return result

    def export_jsonld(self) -> dict:
        graph: List[dict] = [node.to_jsonld() for node in self.nodes.values()]
        graph.extend(edge.to_jsonld() for edge in self.edges)
        return {
            "@context": {
                "id": "@id",
                "type": "@type",
                "edgeType": "ci:edgeType",
                "classification": "ci:classification",
                "tags": "ci:tags",
            },
            "@graph": graph,
        }

    def import_jsonld(self, data: dict, node_factory: Callable[[dict], BaseNode]) -> None:
        self.nodes.clear()
        self.edges.clear()
        pending_edges: List[Edge] = []
        for item in data.get("@graph", []):
            if item.get("@type") == "Edge":
                pending_edges.append(
                    Edge(
                        source=item["source"],
                        target=item["target"],
                        edge_type=EdgeType(item["edgeType"]),
                        metadata={k: v for k, v in item.items() if k not in {"@id", "@type", "source", "target", "edgeType"}},
                    )
                )
            else:
                node = node_factory(item)
                self.upsert_node(node)
        for edge in pending_edges:
            self.add_edge(edge)