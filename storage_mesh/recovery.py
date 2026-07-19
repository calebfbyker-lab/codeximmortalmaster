# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha3_256

from .distributor import DistributionManifest, LocalColdStore
from .sharding import Shard, ShardEngine


@dataclass(frozen=True)
class RecoveryResult:
    asset_id: str
    recovered: bool
    verified_shards: int
    failed_shards: list[str]
    payload: bytes | None


class RecoveryEngine:
    def __init__(self, shard_engine: ShardEngine, store: LocalColdStore) -> None:
        self._shard_engine = shard_engine
        self._store = store

    def recover(
        self,
        manifest: DistributionManifest,
        shard_catalog: dict[str, Shard],
    ) -> RecoveryResult:
        verified: list[Shard] = []
        failed: list[str] = []

        for location in manifest.locations:
            shard = shard_catalog[location.shard_id]
            actual = self._store.get(location)

            if sha3_256(actual).hexdigest() != shard.leaf_hash:
                failed.append(shard.shard_id)
                continue

            verified.append(
                Shard(
                    shard_id=shard.shard_id,
                    index=shard.index,
                    threshold=shard.threshold,
                    total=shard.total,
                    data=actual,
                    leaf_hash=shard.leaf_hash,
                )
            )

            if len(verified) >= manifest.threshold:
                payload = self._shard_engine.reconstruct(verified)
                return RecoveryResult(
                    asset_id=manifest.asset_id,
                    recovered=True,
                    verified_shards=len(verified),
                    failed_shards=failed,
                    payload=payload,
                )

        return RecoveryResult(
            asset_id=manifest.asset_id,
            recovered=False,
            verified_shards=len(verified),
            failed_shards=failed,
            payload=None,
        )