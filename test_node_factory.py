# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from neural_fabric.memory.node_factory import node_from_jsonld
from neural_fabric.memory.schema import ArtifactNode, GraphKind


def test_node_factory_builds_artifact_node() -> None:
    record = {
        "@id": "artifact:test-1",
        "@type": "Artifact",
        "graph": "knowledge",
        "classification": "SENSITIVE",
        "tags": ["test"],
        "hash": "sha3:test",
        "artifact_type": "RepairRecord",
        "cid": "bafy123",
        "nft_ref": "nft:1",
    }

    node = node_from_jsonld(record)

    assert isinstance(node, ArtifactNode)
    assert node.id == "artifact:test-1"
    assert node.graph == GraphKind.KNOWLEDGE
    assert node.hash == "sha3:test"