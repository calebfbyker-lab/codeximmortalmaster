# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from typing import Any, Dict, Type

from .schema import (
    AgentNode,
    AlertClusterNode,
    ArtifactNode,
    BaseNode,
    COAOptionNode,
    EvidenceBundleNode,
    GateDecisionNode,
    GraphKind,
    KeyRotationNode,
    MissionContextNode,
    MissionNode,
    ObservationNode,
    OperationNode,
    ProofArtifactNode,
    StorageShardNode,
    ThreatEventNode,
)

NODE_TYPE_MAP: Dict[str, Type[BaseNode]] = {
    "Agent": AgentNode,
    "ThreatEvent": ThreatEventNode,
    "Artifact": ArtifactNode,
    "Operation": OperationNode,
    "KeyRotation": KeyRotationNode,
    "ProofArtifact": ProofArtifactNode,
    "StorageShard": StorageShardNode,
    "Mission": MissionNode,
    "MissionContext": MissionContextNode,
    "Observation": ObservationNode,
    "COAOption": COAOptionNode,
    "GateDecision": GateDecisionNode,
    "EvidenceBundle": EvidenceBundleNode,
    "AlertCluster": AlertClusterNode,
}


def node_from_jsonld(record: Dict[str, Any]) -> BaseNode:
    node_type = record.get("@type") or record.get("node_type")
    if not node_type:
        raise ValueError("JSON-LD record missing @type")

    model = NODE_TYPE_MAP.get(node_type)
    if model is None:
        raise ValueError(f"Unsupported node type: {node_type}")

    payload = dict(record)
    payload["id"] = payload.pop("@id", payload.get("id"))
    payload["node_type"] = payload.pop("@type", payload.get("node_type"))

    if "graph" in payload and isinstance(payload["graph"], str):
        payload["graph"] = GraphKind(payload["graph"])

    return model(**payload)