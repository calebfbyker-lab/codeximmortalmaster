# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .node_factory import node_from_jsonld


class Neo4jQueryAdapter:
    def __init__(self, driver) -> None:
        self.driver = driver

    def query_nodes(
        self,
        node_type: Optional[str] = None,
        classification: Optional[str] = None,
        tags_any: Optional[list[str]] = None,
        limit: int = 50,
    ) -> List[Any]:
        where = []
        params: Dict[str, Any] = {"limit": limit}

        if node_type:
            where.append("n.node_type = $node_type")
            params["node_type"] = node_type
        if classification:
            where.append("n.classification = $classification")
            params["classification"] = classification
        if tags_any:
            where.append("ANY(tag IN $tags_any WHERE tag IN coalesce(n.tags, []))")
            params["tags_any"] = tags_any

        where_clause = f"WHERE {' AND '.join(where)}" if where else ""
        query = f"""
        MATCH (n:CodexNode)
        {where_clause}
        RETURN n
        LIMIT $limit
        """

        results = []
        with self.driver.session() as session:
            records = session.run(query, **params)
            for record in records:
                props = dict(record["n"])
                results.append(node_from_jsonld(self._props_to_jsonld(props)))
        return results

    def fetch_neighbors(self, node_id: str, relation_type: Optional[str] = None, limit: int = 50) -> List[dict]:
        params: Dict[str, Any] = {"node_id": node_id, "limit": limit}
        rel_filter = ""
        if relation_type:
            rel_filter = "WHERE type(r) = $relation_type"
            params["relation_type"] = relation_type

        query = f"""
        MATCH (a:CodexNode {{id: $node_id}})-[r]->(b:CodexNode)
        {rel_filter}
        RETURN a.id as source, type(r) as relation_type, r.metadata as metadata, b as target
        LIMIT $limit
        """

        results = []
        with self.driver.session() as session:
            records = session.run(query, **params)
            for record in records:
                results.append(
                    {
                        "source": record["source"],
                        "relation_type": record["relation_type"],
                        "metadata": record["metadata"],
                        "target": dict(record["target"]),
                    }
                )
        return results

    @staticmethod
    def _props_to_jsonld(props: Dict[str, Any]) -> Dict[str, Any]:
        data = dict(props)
        data["@id"] = data.pop("id")
        data["@type"] = data.pop("node_type")
        return data