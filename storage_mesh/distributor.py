# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from .sharding import Shard


@dataclass(frozen=True)
class ShardLocation:
    shard_id: str
    provider: str
    locator: str
    region: str


@dataclass(frozen=True)
class DistributionManifest:
    asset_id: str
    threshold: int
    total: int
    merkle_root: str
    locations: list[ShardLocation]


class LocalColdStore:
    def __init__(self, root: str | Path, region: str = "local-airgap") -> None:
        self.root = Path(root)
        self.region = region
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, shard: Shard) -> ShardLocation:
        path = self.root / f"{shard.shard_id}.shard"
        path.write_bytes(shard.data)
        return ShardLocation(
            shard_id=shard.shard_id,
            provider="local-cold-store",
            locator=str(path),
            region=self.region,
        )

    def get(self, location: ShardLocation) -> bytes:
        return Path(location.locator).read_bytes()


class ShardDistributor:
    def __init__(self, stores: list[LocalColdStore]) -> None:
        if not stores:
            raise ValueError("At least one store is required.")
        self._stores = stores

    def distribute(
        self,
        asset_id: str,
        shards: list[Shard],
        merkle_root: str,
    ) -> DistributionManifest:
        locations = [
            self._stores[position % len(self._stores)].put(shard)
            for position, shard in enumerate(shards)
        ]
        return DistributionManifest(
            asset_id=asset_id,
            threshold=shards[0].threshold,
            total=len(shards),
            merkle_root=merkle_root,
            locations=locations,
        )