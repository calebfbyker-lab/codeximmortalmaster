# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from pathlib import Path

from neural_fabric.memory.archivist_service import ArchivistService
from neural_fabric.memory.signer import MockHMACSigner


def test_archivist_service_record_and_restore(tmp_path: Path) -> None:
    signer = MockHMACSigner(b"archivist-test-secret", signer_name="archivist-unit")
    service = ArchivistService(signer=signer)

    action = {
        "id": "evt-100",
        "hash": "sha3-256:evt100",
        "type": "RepairNFT",
        "classification": "SENSITIVE",
        "timestamp": "2026-07-25T07:20:00Z",
        "risk_score": 6.1,
        "summary": "Repair record captured",
        "proof": {
            "proof_hash": "proof-100",
            "public_inputs_hash": "pub-100",
            "proof_type": "Groth16",
            "verifier_ref": "verifier:100",
        },
        "shards": [
            {"index": 1, "merkle_leaf": "leaf-a", "provider": "ipfs", "region": "us-east-1", "integrity_state": "OK"},
        ],
    }

    service.record_action(action, mission_id="mission-100", ooda_cycle=1)

    snapshot_path = tmp_path / "snapshot.json"
    service.save_memory_snapshot(snapshot_path)
    restored = service.restore_memory_snapshot(snapshot_path, require_signature=True)

    assert restored.get_node("artifact:evt-100") is not None
    assert restored.get_node("proof:evt-100") is not None

    service.shutdown()