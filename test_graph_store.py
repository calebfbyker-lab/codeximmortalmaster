# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from neural_fabric.memory.graph_store import MemoryGraphStore
from neural_fabric.memory.schema import ArtifactNode, EdgeType, GraphKind, OperationNode


def test_memory_graph_store_query_filters() -> None:
    store = MemoryGraphStore()

    store.add_node(
        OperationNode(
            id="operation:1",
            graph=GraphKind.KNOWLEDGE,
            classification="SENSITIVE",
            tags=["repair", "critical"],
            playbook="LOCKDOWN_LATTICE",
            trigger="FAULT",
            phases_completed=1,
            outcome="PENDING",
            blast_radius=1.0,
        )
    )
    store.add_node(
        ArtifactNode(
            id="artifact:1",
            graph=GraphKind.KNOWLEDGE,
            classification="SENSITIVE",
            tags=["repair"],
            hash="sha3-256:1",
            artifact_type="RepairNFT",
            cid="bafy1",
            nft_ref="nft:1",
        )
    )
    store.add_edge("operation:1", "artifact:1", EdgeType.GENERATED_BY)

    results = store.query({"node_type": "Artifact", "classification": "SENSITIVE", "tags_any": ["repair"]})

    assert len(results) == 1
    assert results[0].id == "artifact:1"


def test_memory_graph_store_jsonld_round_trip() -> None:
    store = MemoryGraphStore()
    store.add_node(
        ArtifactNode(
            id="artifact:2",
            graph=GraphKind.KNOWLEDGE,
            classification="SENSITIVE",
            tags=["snapshot"],
            hash="sha3-256:2",
            artifact_type="SnapshotRecord",
            cid=None,
            nft_ref=None,
        )
    )

    payload = store.export_jsonld()

    restored = MemoryGraphStore()
    restored.import_jsonld(payload)

    results = restored.query({"node_type": "Artifact", "classification": "SENSITIVE"})
    assert len(results) == 1
    assert results[0].id == "artifact:2"