# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from pathlib import Path

from neural_fabric.memory.knowledge_store import KnowledgeStore
from neural_fabric.memory.node_factory import node_from_jsonld
from neural_fabric.memory.schema import ArtifactNode, GraphKind
from neural_fabric.memory.sync import MemorySync


def test_memory_sync_round_trip(tmp_path: Path) -> None:
    store = KnowledgeStore()
    store.upsert_node(
        ArtifactNode(
            id="artifact:sync-1",
            graph=GraphKind.KNOWLEDGE,
            classification="SENSITIVE",
            tags=["sync"],
            hash="sha3-256:sync",
            artifact_type="SnapshotRecord",
            cid="bafy-sync",
            nft_ref="nft:sync-1",
        )
    )

    sync = MemorySync(signer=lambda data: f"sig:{len(data)}", signer_name="test-signer")
    snapshot_path = tmp_path / "memory_snapshot.json"

    snapshot = sync.save_snapshot(store, snapshot_path)
    restored = sync.restore_store(snapshot_path)

    assert snapshot.snapshot_id.startswith("snapshot:")
    assert snapshot.signature is not None
    assert restored.get_node("artifact:sync-1") is not None


def test_memory_sync_canonical_json_is_stable() -> None:
    store = KnowledgeStore()
    store.upsert_node(
        ArtifactNode(
            id="artifact:stable-1",
            graph=GraphKind.KNOWLEDGE,
            classification="SENSITIVE",
            tags=["stable"],
            hash="sha3-256:stable",
            artifact_type="StableRecord",
            cid=None,
            nft_ref=None,
        )
    )

    sync = MemorySync()
    a = sync.export_canonical_json(store)
    b = sync.export_canonical_json(store)

    assert a == b