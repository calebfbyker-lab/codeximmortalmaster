# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .knowledge_store import KnowledgeStore
from .node_factory import node_from_jsonld
from .signer import SignatureEnvelope, SnapshotSigner


@dataclass
class MemorySnapshot:
    snapshot_id: str
    created_at: str
    graph_root: str
    signature: Optional[SignatureEnvelope]
    payload: Dict[str, Any]


class MemorySync:
    def __init__(self, signer: Optional[SnapshotSigner] = None) -> None:
        self.signer = signer

    def export_canonical_json(self, store: KnowledgeStore) -> str:
        payload = store.export_jsonld()
        normalized = self._normalize(payload)
        return json.dumps(normalized, sort_keys=True, separators=(",", ":"))

    def compute_graph_root(self, store: KnowledgeStore) -> str:
        canonical = self.export_canonical_json(store).encode("utf-8")
        return hashlib.sha3_256(canonical).hexdigest()

    def create_snapshot(self, store: KnowledgeStore) -> MemorySnapshot:
        canonical = self.export_canonical_json(store).encode("utf-8")
        graph_root = hashlib.sha3_256(canonical).hexdigest()
        created_at = datetime.now(timezone.utc).isoformat()
        snapshot_id = f"snapshot:{graph_root[:16]}"
        signature = self.signer.sign(canonical) if self.signer else None
        payload = json.loads(canonical.decode("utf-8"))
        return MemorySnapshot(
            snapshot_id=snapshot_id,
            created_at=created_at,
            graph_root=graph_root,
            signature=signature,
            payload=payload,
        )

    def save_snapshot(self, store: KnowledgeStore, path: str | Path) -> MemorySnapshot:
        snapshot = self.create_snapshot(store)
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(
                {
                    "snapshot_id": snapshot.snapshot_id,
                    "created_at": snapshot.created_at,
                    "graph_root": snapshot.graph_root,
                    "signature": snapshot.signature.to_dict() if snapshot.signature else None,
                    "payload": snapshot.payload,
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        return snapshot

    def load_snapshot(self, path: str | Path) -> MemorySnapshot:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        envelope = None
        if data.get("signature"):
            envelope = SignatureEnvelope(**data["signature"])
        return MemorySnapshot(
            snapshot_id=data["snapshot_id"],
            created_at=data["created_at"],
            graph_root=data["graph_root"],
            signature=envelope,
            payload=data["payload"],
        )

    def verify_snapshot_signature(self, snapshot: MemorySnapshot) -> bool:
        if not self.signer or not snapshot.signature:
            return False
        canonical = json.dumps(
            self._normalize(snapshot.payload),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return self.signer.verify(canonical, snapshot.signature)

    def restore_store(self, path: str | Path, require_signature: bool = False) -> KnowledgeStore:
        snapshot = self.load_snapshot(path)
        if require_signature:
            if not snapshot.signature:
                raise ValueError("Snapshot signature required but missing")
            if not self.verify_snapshot_signature(snapshot):
                raise ValueError("Snapshot signature verification failed")

        store = KnowledgeStore()
        store.import_jsonld(snapshot.payload, node_from_jsonld)
        expected_root = self.compute_graph_root(store)
        if expected_root != snapshot.graph_root:
            raise ValueError("Snapshot integrity verification failed")
        return store

    def _normalize(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {k: self._normalize(value[k]) for k in sorted(value)}
        if isinstance(value, list):
            if value and all(isinstance(item, dict) for item in value):
                return [self._normalize(item) for item in sorted(value, key=self._sort_key)]
            return [self._normalize(item) for item in value]
        return value

    @staticmethod
    def _sort_key(item: Dict[str, Any]) -> str:
        return str(item.get("@id", item.get("id", "")))