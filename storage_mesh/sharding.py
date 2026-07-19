# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha3_256
from typing import Protocol


@dataclass(frozen=True)
class Shard:
    shard_id: str
    index: int
    threshold: int
    total: int
    data: bytes
    leaf_hash: str


class SecretSharingBackend(Protocol):
    def split(self, payload: bytes, threshold: int, total: int) -> list[bytes]: ...
    def combine(self, shares: list[bytes]) -> bytes: ...


class ShardEngine:
    """Backend-agnostic threshold sharding over sealed payload bytes."""

    def __init__(self, backend: SecretSharingBackend) -> None:
        self._backend = backend

    def shard(self, sealed_bytes: bytes, threshold: int, total: int) -> list[Shard]:
        if not 2 <= threshold <= total:
            raise ValueError("Require 2 <= threshold <= total.")

        raw_shares = self._backend.split(sealed_bytes, threshold, total)
        return [
            Shard(
                shard_id=sha3_256(
                    f"{index}|{share.hex()}".encode()
                ).hexdigest(),
                index=index,
                threshold=threshold,
                total=total,
                data=share,
                leaf_hash=sha3_256(share).hexdigest(),
            )
            for index, share in enumerate(raw_shares, start=1)
        ]

    def reconstruct(self, shards: list[Shard]) -> bytes:
        if not shards:
            raise ValueError("At least one shard is required.")

        threshold = shards[0].threshold
        if len(shards) < threshold:
            raise ValueError(f"Need {threshold} shards; received {len(shards)}.")

        if len({shard.index for shard in shards}) != len(shards):
            raise ValueError("Duplicate shard index detected.")

        return self._backend.combine([shard.data for shard in shards])