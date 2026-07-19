# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha3_256

from .sharding import Shard


def _hash(data: bytes) -> bytes:
    return sha3_256(data).digest()


@dataclass(frozen=True)
class IntegrityReport:
    shard_id: str
    expected_hash: str
    actual_hash: str
    verified: bool
    merkle_root: str


class MerkleTree:
    def __init__(self, leaves: list[bytes]) -> None:
        if not leaves:
            raise ValueError("Merkle tree requires at least one leaf.")
        self._leaves = [_hash(leaf) for leaf in leaves]
        self._root = self._build(self._leaves)

    @staticmethod
    def _build(nodes: list[bytes]) -> bytes:
        current = nodes
        while len(current) > 1:
            if len(current) % 2:
                current.append(current[-1])
            current = [
                _hash(current[i] + current[i + 1])
                for i in range(0, len(current), 2)
            ]
        return current[0]

    @property
    def root_hex(self) -> str:
        return self._root.hex()


class IntegrityMonitor:
    def __init__(self, shards: list[Shard]) -> None:
        self._shards = {shard.shard_id: shard for shard in shards}
        self._tree = MerkleTree([shard.data for shard in shards])

    def verify_shard(self, shard_id: str, retrieved_data: bytes) -> IntegrityReport:
        shard = self._shards[shard_id]
        actual = sha3_256(retrieved_data).hexdigest()

        return IntegrityReport(
            shard_id=shard_id,
            expected_hash=shard.leaf_hash,
            actual_hash=actual,
            verified=(actual == shard.leaf_hash),
            merkle_root=self._tree.root_hex,
        )

    def audit(self, fetch: callable) -> list[IntegrityReport]:
        return [
            self.verify_shard(shard_id, fetch(shard_id))
            for shard_id in self._shards
        ]