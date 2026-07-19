# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha3_256
from typing import Callable
import threading
import time

from .sharding import Shard


def _hash(data: bytes) -> bytes:
    return sha3_256(data).digest()


@dataclass(frozen=True)
class MerkleProof:
    leaf_index: int
    siblings: list[str]
    root: str


@dataclass(frozen=True)
class IntegrityResult:
    shard_id: str
    expected_hash: str
    actual_hash: str
    verified: bool
    severity: str


@dataclass(frozen=True)
class AuditReport:
    root: str
    total_shards: int
    failures: int
    results: list[IntegrityResult]


class MerkleTree:
    def __init__(self, leaves: list[bytes]) -> None:
        if not leaves:
            raise ValueError("At least one leaf is required.")
        self._leaf_hashes = [_hash(leaf) for leaf in leaves]
        self._levels = [self._leaf_hashes]
        self._build()

    def _build(self) -> None:
        current = self._leaf_hashes
        while len(current) > 1:
            if len(current) % 2:
                current = current + [current[-1]]
            current = [
                _hash(current[i] + current[i + 1]) for i in range(0, len(current), 2)
            ]
            self._levels.append(current)

    @property
    def root(self) -> str:
        return self._levels[-1][0].hex()

    def get_proof(self, leaf_index: int) -> MerkleProof:
        siblings: list[str] = []
        idx = leaf_index
        for level in self._levels[:-1]:
            pair_idx = idx ^ 1
            if pair_idx < len(level):
                siblings.append(level[pair_idx].hex())
            idx //= 2
        return MerkleProof(leaf_index=leaf_index, siblings=siblings, root=self.root)


class TamperAlarm:
    def __init__(self, notifier: Callable[[dict], None] | None = None) -> None:
        self._notifier = notifier

    def on_tamper_detected(
        self, shard_id: str, expected_hash: str, actual_hash: str, severity: str
    ) -> None:
        event = {
            "type": "tamper-detected",
            "shard_id": shard_id,
            "expected_hash": expected_hash,
            "actual_hash": actual_hash,
            "severity": severity,
            "action": "LOCKDOWN-LATTICE" if severity == "CRITICAL" else "ALERT",
        }
        if self._notifier:
            self._notifier(event)


class ShardIntegrityMonitor:
    def __init__(
        self,
        shards: list[Shard],
        fetcher: Callable[[str], bytes],
        notifier: Callable[[dict], None] | None = None,
    ) -> None:
        self._shards = {shard.shard_id: shard for shard in shards}
        self._ordered = list(shards)
        self._tree = MerkleTree([shard.data for shard in shards])
        self._fetcher = fetcher
        self._alarm = TamperAlarm(notifier)
        self._stop = False

    def register_shard(self, shard: Shard) -> str:
        self._shards[shard.shard_id] = shard
        self._ordered.append(shard)
        self._tree = MerkleTree([item.data for item in self._ordered])
        return shard.leaf_hash

    def verify_shard(self, shard_id: str) -> IntegrityResult:
        shard = self._shards[shard_id]
        data = self._fetcher(shard_id)
        actual = sha3_256(data).hexdigest()
        ok = actual == shard.leaf_hash
        severity = "LOW" if ok else "CRITICAL"

        if not ok:
            self._alarm.on_tamper_detected(shard_id, shard.leaf_hash, actual, severity)

        return IntegrityResult(
            shard_id=shard_id,
            expected_hash=shard.leaf_hash,
            actual_hash=actual,
            verified=ok,
            severity=severity,
        )

    def run_full_audit(self) -> AuditReport:
        results = [self.verify_shard(shard.shard_id) for shard in self._ordered]
        failures = sum(1 for result in results if not result.verified)
        return AuditReport(
            root=self._tree.root,
            total_shards=len(results),
            failures=failures,
            results=results,
        )

    def schedule_audit(self, interval_hours: int) -> threading.Thread:
        interval_seconds = max(1, interval_hours) * 3600

        def loop() -> None:
            while not self._stop:
                self.run_full_audit()
                time.sleep(interval_seconds)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
        return thread

    def stop(self) -> None:
        self._stop = True