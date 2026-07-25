# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field


class GraphKind(str, Enum):
    KNOWLEDGE = "knowledge"
    CONTEXT = "context"


class EdgeType(str, Enum):
    GENERATED_BY = "GENERATED_BY"
    SIGNED_BY = "SIGNED_BY"
    ATTESTED_BY = "ATTESTED_BY"
    MINTED_AS = "MINTED_AS"
    SHARDED_INTO = "SHARDED_INTO"
    STORED_AT = "STORED_AT"
    REFERENCES_PROOF = "REFERENCES_PROOF"
    TRIGGERED = "TRIGGERED"
    OBSERVED_IN = "OBSERVED_IN"
    SUPPORTS_COA = "SUPPORTS_COA"
    ESCALATED_TO = "ESCALATED_TO"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    ACTIVE_IN_CYCLE = "ACTIVE_IN_CYCLE"
    SUPERSEDES = "SUPERSEDES"


class BaseNode(BaseModel):
    id: str
    graph: GraphKind
    node_type: str
    classification: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

    def to_jsonld(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["@id"] = data.pop("id")
        data["@type"] = data.pop("node_type")
        return data


class AgentNode(BaseNode):
    node_type: Literal["Agent"] = "Agent"
    role: str
    version: Optional[str] = None
    trust_score: float = 0.0
    status: str = "ACTIVE"


class ThreatEventNode(BaseNode):
    node_type: Literal["ThreatEvent"] = "ThreatEvent"
    timestamp: str
    signal: str
    severity: float
    resolution: Optional[str] = None


class ArtifactNode(BaseNode):
    node_type: Literal["Artifact"] = "Artifact"
    hash: str
    artifact_type: str
    cid: Optional[str] = None
    nft_ref: Optional[str] = None


class OperationNode(BaseNode):
    node_type: Literal["Operation"] = "Operation"
    playbook: str
    trigger: str
    phases_completed: int = 0
    outcome: Optional[str] = None
    blast_radius: float = 0.0


class KeyRotationNode(BaseNode):
    node_type: Literal["KeyRotation"] = "KeyRotation"
    algorithm: str
    before_fingerprint: str
    after_fingerprint: str
    ceremony_id: str


class ProofArtifactNode(BaseNode):
    node_type: Literal["ProofArtifact"] = "ProofArtifact"
    proof_type: str
    proof_hash: str
    public_inputs_hash: str
    verifier_ref: Optional[str] = None


class StorageShardNode(BaseNode):
    node_type: Literal["StorageShard"] = "StorageShard"
    shard_index: int
    merkle_leaf: str
    provider: str
    region: str
    integrity_state: str


class MissionNode(BaseNode):
    node_type: Literal["Mission"] = "Mission"
    mission_type: str
    start_time: str
    end_time: Optional[str] = None
    result: Optional[str] = None


class MissionContextNode(BaseNode):
    node_type: Literal["MissionContext"] = "MissionContext"
    mission_id: str
    ooda_cycle: int
    status: str
    expires_at: Optional[str] = None


class ObservationNode(BaseNode):
    node_type: Literal["Observation"] = "Observation"
    source: str
    summary: str
    risk_score: float
    observed_at: str


class COAOptionNode(BaseNode):
    node_type: Literal["COAOption"] = "COAOption"
    label: str
    confidence: float
    blast_radius: float
    recommended: bool = False


class GateDecisionNode(BaseNode):
    node_type: Literal["GateDecision"] = "GateDecision"
    gate_type: str
    required: bool
    approver_role: str
    decision: str
    expires_at: Optional[str] = None
    rationale: Optional[str] = None


class EvidenceBundleNode(BaseNode):
    node_type: Literal["EvidenceBundle"] = "EvidenceBundle"
    bundle_hash: str
    artifact_refs: list[str] = Field(default_factory=list)
    alert_count: int
    created_at: str


class AlertClusterNode(BaseNode):
    node_type: Literal["AlertCluster"] = "AlertCluster"
    domain: str
    severity_max: float
    active: bool
    first_seen: str
    last_seen: str


class Edge(BaseModel):
    source: str
    target: str
    edge_type: EdgeType
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_jsonld(self) -> Dict[str, Any]:
        return {
            "@id": f"edge:{self.source}->{self.target}:{self.edge_type.value}",
            "@type": "Edge",
            "source": self.source,
            "target": self.target,
            "edgeType": self.edge_type.value,
            **self.metadata,
        }