# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional
from .schema import BaseNode, Edge, EdgeType, GraphKind


def _parse_ts(ts: str) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


class ContextStore:
    def __init__(self) -> None:
        self.nodes: Dict[str, BaseNode] = {}
        self.edges: List[Edge] = []

    def upsert_node(self, node: BaseNode) -> None:
        if node.graph != GraphKind.CONTEXT:
            raise ValueError("Node must belong to context graph")
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise KeyError("Both edge endpoints must exist in the context graph")
        self.edges.append(edge)

    def get_node(self, node_id: str) -> Optional[BaseNode]:
        return self.nodes.get(node_id)

    def get_active_nodes(self) -> List[BaseNode]:
        now = datetime.now(timezone.utc)
        active: List[BaseNode] = []
        for node in self.nodes.values():
            expires_at = getattr(node, "expires_at", None)
            parsed = _parse_ts(expires_at) if expires_at else None
            if parsed is None or parsed >= now:
                active.append(node)
        return active

    def prune_expired(self) -> List[str]:
        now = datetime.now(timezone.utc)
        expired_ids: List[str] = []
        for node_id, node in list(self.nodes.items()):
            expires_at = getattr(node, "expires_at", None)
            parsed = _parse_ts(expires_at) if expires_at else None
            if parsed is not None and parsed < now:
                expired_ids.append(node_id)
                del self.nodes[node_id]
        if expired_ids:
            self.edges = [e for e in self.edges if e.source not in expired_ids and e.target not in expired_ids]
        return expired_ids

    def replace_cycle(self, mission_context_id: str, replacement_node_id: str) -> None:
        if mission_context_id in self.nodes and replacement_node_id in self.nodes:
            self.edges.append(
                Edge(source=mission_context_id, target=replacement_node_id, edge_type=EdgeType.SUPERSEDES)
            )

    def clear(self) -> None:
        self.nodes.clear()
        self.edges.clear()