# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# Minimal key vault abstraction. Replace backend for production use.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from hashlib import sha3_256


@dataclass(frozen=True)
class StoredKey:
    key_id: str
    algorithm: str
    created_at: datetime
    payload: bytes


class KeyStoreBackend(Protocol):
    def put(self, key_id: str, payload: bytes) -> None: ...
    def get(self, key_id: str) -> bytes | None: ...
    def delete(self, key_id: str) -> None: ...
    def list_ids(self) -> list[str]: ...


class InMemoryKeyStoreBackend:
    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}

    def put(self, key_id: str, payload: bytes) -> None:
        self._store[key_id] = payload

    def get(self, key_id: str) -> bytes | None:
        return self._store.get(key_id)

    def delete(self, key_id: str) -> None:
        self._store.pop(key_id, None)

    def list_ids(self) -> list[str]:
        return list(self._store.keys())


class KeyVault:
    """Thin wrapper around a backend that knows how to seal keys."""

    def __init__(self, backend: KeyStoreBackend | None = None) -> None:
        self._backend = backend or InMemoryKeyStoreBackend()
        self._meta: dict[str, StoredKey] = {}

    def store_key(self, algorithm: str, raw_key: bytes) -> StoredKey:
        key_id = sha3_256(raw_key).hexdigest()
        now = datetime.utcnow()
        record = StoredKey(
            key_id=key_id,
            algorithm=algorithm,
            created_at=now,
            payload=b"",  # not stored here; backend holds actual bytes
        )
        self._backend.put(key_id, raw_key)
        self._meta[key_id] = record
        return record

    def retrieve_key(self, key_id: str) -> bytes | None:
        return self._backend.get(key_id)

    def delete_key(self, key_id: str) -> None:
        self._backend.delete(key_id)
        self._meta.pop(key_id, None)

    def list_keys(self) -> list[StoredKey]:
        return list(self._meta.values())