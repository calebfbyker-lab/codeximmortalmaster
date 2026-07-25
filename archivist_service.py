# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from .context_store import ContextStore
from .graph_store import MemoryGraphStore
from .knowledge_store import KnowledgeStore
from .neo4j_query import Neo4jQueryAdapter
from .sync import MemorySync
from resource_engine.graph_bridge import GraphBridge


class ArchivistService:
    def __init__(
        self,
        signer=None,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
    ) -> None:
        self.knowledge = KnowledgeStore()
        self.context = ContextStore()
        self.bridge = GraphBridge(self.knowledge, self.context)
        self.sync = MemorySync(signer=signer)
        self.memory_graph = MemoryGraphStore(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password,
        )
        self.neo4j_query = Neo4jQueryAdapter(self.memory_graph.driver) if self.memory_graph.driver else None

    def record_action(self, action: Dict[str, Any], mission_id: str, ooda_cycle: int) -> None:
        self.bridge.emit_knowledge_event(action)
        self.bridge.emit_context_event(action, mission_id=mission_id, ooda_cycle=ooda_cycle)

        for node in self.knowledge.nodes.values():
            self.memory_graph.add_node(node)
        for edge in self.knowledge.edges:
            if edge.source in self.memory_graph.graph and edge.target in self.memory_graph.graph:
                relation_exists = self.memory_graph.graph.has_edge(edge.source, edge.target)
                if not relation_exists:
                    self.memory_graph.add_edge(edge.source, edge.target, edge.edge_type, edge.metadata)

    def save_memory_snapshot(self, path: str | Path):
        return self.sync.save_snapshot(self.knowledge, path)

    def restore_memory_snapshot(self, path: str | Path, require_signature: bool = False) -> KnowledgeStore:
        restored = self.sync.restore_store(path, require_signature=require_signature)
        self.knowledge = restored
        return restored

    def query_memory(self, node_type: Optional[str] = None, classification: Optional[str] = None, tags_any: Optional[list[str]] = None, limit: int = 50):
        if self.neo4j_query:
            return self.neo4j_query.query_nodes(
                node_type=node_type,
                classification=classification,
                tags_any=tags_any,
                limit=limit,
            )
        return self.memory_graph.query(
            {
                "node_type": node_type,
                "classification": classification,
                "tags_any": tags_any,
                "limit": limit,
            }
        )

    def shutdown(self) -> None:
        self.memory_graph.close()