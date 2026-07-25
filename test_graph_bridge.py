# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from neural_fabric.memory.context_store import ContextStore
from neural_fabric.memory.knowledge_store import KnowledgeStore
from neural_fabric.memory.schema import EdgeType
from resource_engine.graph_bridge import GraphBridge


def test_graph_bridge_emits_proof_and_shards() -> None:
    knowledge = KnowledgeStore()
    context = ContextStore()
    bridge = GraphBridge(knowledge, context)

    action = {
        "id": "evt-001",
        "hash": "sha3-256:abc123",
        "type": "RepairRecord",
        "classification": "SENSITIVE",
        "timestamp": "2026-07-25T07:00:00Z",
        "risk_score": 4.2,
        "proof": {
            "proof_hash": "proofhash001",
            "public_inputs_hash": "pub001",
            "proof_type": "Groth16",
            "verifier_ref": "verifier:v1",
        },
        "shards": [
            {"index": 1, "merkle_leaf": "leaf1", "provider": "ipfs", "region": "us-east-1", "integrity_state": "OK"},
            {"index": 2, "merkle_leaf": "leaf2", "provider": "arweave", "region": "us-west-2", "integrity_state": "OK"},
        ],
    }

    bridge.emit_knowledge_event(action)

    assert "artifact:evt-001" in knowledge.nodes
    assert "proof:evt-001" in knowledge.nodes
    assert "shard:evt-001:1" in knowledge.nodes
    assert "shard:evt-001:2" in knowledge.nodes

    edge_types = {(e.source, e.target, e.edge_type) for e in knowledge.edges}
    assert ("artifact:evt-001", "proof:evt-001", EdgeType.REFERENCES_PROOF) in edge_types
    assert ("artifact:evt-001", "shard:evt-001:1", EdgeType.SHARDED_INTO) in edge_types
    assert ("artifact:evt-001", "shard:evt-001:2", EdgeType.STORED_AT) in edge_types


def test_graph_bridge_requires_human_gate_for_high_risk_action() -> None:
    knowledge = KnowledgeStore()
    context = ContextStore()
    bridge = GraphBridge(knowledge, context)

    action = {
        "id": "evt-002",
        "hash": "sha3-256:def456",
        "type": "CommandFabricRecord",
        "classification": "SENSITIVE",
        "timestamp": "2026-07-25T07:05:00Z",
        "risk_score": 9.1,
        "summary": "Critical navigation anomaly",
        "gate_type": "NAVIGATION",
        "coa_options": [
            {"label": "Isolate affected subsystem", "confidence": 0.91, "blast_radius": 2.0, "recommended": True},
            {"label": "Continue passive monitoring", "confidence": 0.44, "blast_radius": 0.5, "recommended": False},
        ],
    }

    bridge.emit_context_event(action, mission_id="mission-42", ooda_cycle=3)

    assert "context:mission-42:3" in context.nodes
    assert "obs:evt-002" in context.nodes
    assert "gate:evt-002" in context.nodes
    assert "coa:evt-002:1" in context.nodes
    assert "coa:evt-002:2" in context.nodes

    gate = context.nodes["gate:evt-002"]
    assert gate.required is True
    assert gate.decision == "PENDING_HUMAN"

    edge_types = {(e.source, e.target, e.edge_type) for e in context.edges}
    assert ("obs:evt-002", "gate:evt-002", EdgeType.ESCALATED_TO) in edge_types
    assert ("obs:evt-002", "coa:evt-002:1", EdgeType.SUPPORTS_COA) in edge_types