# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from typing import Any, Dict
from neural_fabric.memory.schema import (
    AlertClusterNode,
    ArtifactNode,
    COAOptionNode,
    Edge,
    EdgeType,
    EvidenceBundleNode,
    GateDecisionNode,
    GraphKind,
    MissionContextNode,
    ObservationNode,
    OperationNode,
    ProofArtifactNode,
    StorageShardNode,
    ThreatEventNode,
)
from neural_fabric.memory.knowledge_store import KnowledgeStore
from neural_fabric.memory.context_store import ContextStore

HUMAN_GATE_DOMAINS = {"KINETIC", "BIO", "SPACE", "TOP_SECRET", "TS_SCI"}
HUMAN_GATE_OPERATION_TYPES = {"MASTER_SHARD_ROTATION", "RED_TEAM_LEVEL_5", "RED_TEAM_LEVEL_6"}


class GraphBridge:
    def __init__(self, knowledge: KnowledgeStore, context: ContextStore) -> None:
        self.knowledge = knowledge
        self.context = context

    def emit_knowledge_event(self, action: Dict[str, Any]) -> None:
        operation = OperationNode(
            id=f"operation:{action['id']}",
            graph=GraphKind.KNOWLEDGE,
            classification=action.get("classification"),
            tags=action.get("tags", []),
            playbook=action.get("playbook", "UNSPECIFIED"),
            trigger=action.get("trigger", action.get("type", "RESOURCE_ACTION")),
            phases_completed=action.get("phases_completed", 1),
            outcome=action.get("outcome"),
            blast_radius=float(action.get("blast_radius", 0.0)),
        )
        self.knowledge.upsert_node(operation)

        artifact = ArtifactNode(
            id=f"artifact:{action['id']}",
            graph=GraphKind.KNOWLEDGE,
            classification=action.get("classification"),
            tags=action.get("tags", []),
            hash=action["hash"],
            artifact_type=action.get("type", "ResourceAction"),
            cid=action.get("cid"),
            nft_ref=action.get("nft_ref"),
        )
        self.knowledge.upsert_node(artifact)
        self.knowledge.add_edge(Edge(source=operation.id, target=artifact.id, edge_type=EdgeType.GENERATED_BY))

        if action.get("threat_signal"):
            threat = ThreatEventNode(
                id=f"threat:{action['id']}",
                graph=GraphKind.KNOWLEDGE,
                classification=action.get("classification"),
                tags=action.get("tags", []),
                timestamp=action.get("timestamp", ""),
                signal=action["threat_signal"],
                severity=float(action.get("risk_score", 0.0)),
                resolution=action.get("resolution"),
            )
            self.knowledge.upsert_node(threat)
            self.knowledge.add_edge(Edge(source=threat.id, target=operation.id, edge_type=EdgeType.TRIGGERED))

        if action.get("proof"):
            proof = action["proof"]
            proof_node = ProofArtifactNode(
                id=f"proof:{action['id']}",
                graph=GraphKind.KNOWLEDGE,
                classification=action.get("classification"),
                tags=action.get("tags", []),
                proof_type=proof.get("proof_type", "Groth16"),
                proof_hash=proof["proof_hash"],
                public_inputs_hash=proof.get("public_inputs_hash", ""),
                verifier_ref=proof.get("verifier_ref"),
            )
            self.knowledge.upsert_node(proof_node)
            self.knowledge.add_edge(Edge(source=artifact.id, target=proof_node.id, edge_type=EdgeType.REFERENCES_PROOF))
            self.knowledge.add_edge(Edge(source=artifact.id, target=proof_node.id, edge_type=EdgeType.ATTESTED_BY))

        for shard in action.get("shards", []):
            shard_node = StorageShardNode(
                id=f"shard:{action['id']}:{shard['index']}",
                graph=GraphKind.KNOWLEDGE,
                classification=action.get("classification"),
                tags=action.get("tags", []),
                shard_index=int(shard["index"]),
                merkle_leaf=shard["merkle_leaf"],
                provider=shard.get("provider", "unknown"),
                region=shard.get("region", "unknown"),
                integrity_state=shard.get("integrity_state", "UNKNOWN"),
            )
            self.knowledge.upsert_node(shard_node)
            self.knowledge.add_edge(Edge(source=artifact.id, target=shard_node.id, edge_type=EdgeType.SHARDED_INTO))
            self.knowledge.add_edge(Edge(source=artifact.id, target=shard_node.id, edge_type=EdgeType.STORED_AT))

    def emit_context_event(self, action: Dict[str, Any], mission_id: str, ooda_cycle: int) -> None:
        context_id = f"context:{mission_id}:{ooda_cycle}"
        ctx = MissionContextNode(
            id=context_id,
            graph=GraphKind.CONTEXT,
            classification=action.get("classification"),
            tags=action.get("tags", []),
            mission_id=mission_id,
            ooda_cycle=ooda_cycle,
            status=action.get("status", "ACTIVE"),
            expires_at=action.get("expires_at"),
        )
        self.context.upsert_node(ctx)

        obs = ObservationNode(
            id=f"obs:{action['id']}",
            graph=GraphKind.CONTEXT,
            classification=action.get("classification"),
            tags=action.get("tags", []),
            source=action.get("source", "resource-engine"),
            summary=action.get("summary", ""),
            risk_score=float(action.get("risk_score", 0.0)),
            observed_at=action.get("timestamp", ""),
        )
        self.context.upsert_node(obs)
        self.context.add_edge(Edge(source=obs.id, target=ctx.id, edge_type=EdgeType.OBSERVED_IN))
        self.context.add_edge(Edge(source=obs.id, target=ctx.id, edge_type=EdgeType.ACTIVE_IN_CYCLE))

        if action.get("evidence_bundle"):
            bundle = action["evidence_bundle"]
            evidence = EvidenceBundleNode(
                id=f"evidence:{action['id']}",
                graph=GraphKind.CONTEXT,
                classification=action.get("classification"),
                tags=action.get("tags", []),
                bundle_hash=bundle["bundle_hash"],
                artifact_refs=bundle.get("artifact_refs", []),
                alert_count=int(bundle.get("alert_count", 0)),
                created_at=bundle.get("created_at", action.get("timestamp", "")),
            )
            self.context.upsert_node(evidence)
            self.context.add_edge(Edge(source=evidence.id, target=ctx.id, edge_type=EdgeType.OBSERVED_IN))

        for idx, coa in enumerate(action.get("coa_options", []), start=1):
            coa_node = COAOptionNode(
                id=f"coa:{action['id']}:{idx}",
                graph=GraphKind.CONTEXT,
                classification=action.get("classification"),
                tags=action.get("tags", []),
                label=coa["label"],
                confidence=float(coa.get("confidence", 0.0)),
                blast_radius=float(coa.get("blast_radius", 0.0)),
                recommended=bool(coa.get("recommended", False)),
            )
            self.context.upsert_node(coa_node)
            self.context.add_edge(Edge(source=obs.id, target=coa_node.id, edge_type=EdgeType.SUPPORTS_COA))

        gate_required = self._requires_human_gate(action)
        gate_node = GateDecisionNode(
            id=f"gate:{action['id']}",
            graph=GraphKind.CONTEXT,
            classification=action.get("classification"),
            tags=action.get("tags", []),
            gate_type=action.get("gate_type", "GENERAL"),
            required=gate_required,
            approver_role=action.get("approver_role", "COMMANDER" if gate_required else "AUTO"),
            decision=action.get("decision", "PENDING_HUMAN" if gate_required else "AUTOMATED"),
            expires_at=action.get("gate_expires_at"),
            rationale=action.get("gate_rationale"),
        )
        self.context.upsert_node(gate_node)
        self.context.add_edge(Edge(source=obs.id, target=gate_node.id, edge_type=EdgeType.ESCALATED_TO))
        self.context.add_edge(Edge(source=gate_node.id, target=ctx.id, edge_type=EdgeType.REQUIRES_APPROVAL, metadata={"required": gate_required}))

        if action.get("alert_cluster"):
            cluster = action["alert_cluster"]
            cluster_node = AlertClusterNode(
                id=f"cluster:{action['id']}",
                graph=GraphKind.CONTEXT,
                classification=action.get("classification"),
                tags=action.get("tags", []),
                domain=cluster.get("domain", action.get("gate_type", "GENERAL")),
                severity_max=float(cluster.get("severity_max", action.get("risk_score", 0.0))),
                active=bool(cluster.get("active", True)),
                first_seen=cluster.get("first_seen", action.get("timestamp", "")),
                last_seen=cluster.get("last_seen", action.get("timestamp", "")),
            )
            self.context.upsert_node(cluster_node)
            self.context.add_edge(Edge(source=cluster_node.id, target=ctx.id, edge_type=EdgeType.ACTIVE_IN_CYCLE))

    def _requires_human_gate(self, action: Dict[str, Any]) -> bool:
        score = float(action.get("risk_score", 0.0))
        classification = str(action.get("classification", ""))
        gate_type = str(action.get("gate_type", ""))
        operation_type = str(action.get("operation_type", ""))
        return (
            score > 8.5
            or classification in HUMAN_GATE_DOMAINS
            or gate_type in HUMAN_GATE_DOMAINS
            or operation_type in HUMAN_GATE_OPERATION_TYPES
        )