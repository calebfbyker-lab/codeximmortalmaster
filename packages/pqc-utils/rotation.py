# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# PQC key rotation lifecycle (session, signing, master, custody).

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha3_256
from typing import Literal

from .kem import KemKeyPair, KyberKEM
from .signing import SigningKeyPair, DilithiumSigner

RotationKeyType = Literal["session", "signing", "master", "custody"]


@dataclass(frozen=True)
class RotationEvent:
    """Record of a key rotation suitable for NFT provenance."""
    key_type: RotationKeyType
    algorithm: str
    before_fingerprint: str | None
    after_fingerprint: str
    created_at: datetime

    @property
    def event_id(self) -> str:
        payload = (
            f"{self.key_type}|{self.algorithm}|"
            f"{self.before_fingerprint or ''}|{self.after_fingerprint}|"
            f"{self.created_at.isoformat()}"
        ).encode("utf-8")
        return sha3_256(payload).hexdigest()


@dataclass
class KeyRecord:
    key_type: RotationKeyType
    algorithm: str
    fingerprint: str
    public_key: bytes
    secret_key: bytes
    created_at: datetime
    expires_at: datetime


class KeyRotationManager:
    """Schedule-aware key rotation manager for PQC keys."""

    def __init__(
        self,
        session_lifetime: timedelta = timedelta(hours=24),
        signing_lifetime: timedelta = timedelta(days=7),
        master_lifetime: timedelta = timedelta(days=30),
        custody_lifetime: timedelta = timedelta(days=90),
    ) -> None:
        self._session_lifetime = session_lifetime
        self._signing_lifetime = signing_lifetime
        self._master_lifetime = master_lifetime
        self._custody_lifetime = custody_lifetime
        self._keys: dict[RotationKeyType, KeyRecord] = {}
        self._history: list[RotationEvent] = []

    # Public API --------------------------------------------------------------

    def get_active_key(self, key_type: RotationKeyType) -> KeyRecord | None:
        record = self._keys.get(key_type)
        if record and record.expires_at > datetime.utcnow():
            return record
        return None

    def get_rotation_history(self) -> list[RotationEvent]:
        return list(self._history)

    def rotate_now(self, key_type: RotationKeyType) -> RotationEvent:
        """Rotate a key immediately and record the event."""
        before = self._keys.get(key_type)
        new_record = self._generate_key_record(key_type)
        self._keys[key_type] = new_record

        event = RotationEvent(
            key_type=key_type,
            algorithm=new_record.algorithm,
            before_fingerprint=before.fingerprint if before else None,
            after_fingerprint=new_record.fingerprint,
            created_at=datetime.utcnow(),
        )
        self._history.append(event)
        return event

    # Internal helpers --------------------------------------------------------

    def _lifetime_for(self, key_type: RotationKeyType) -> timedelta:
        match key_type:
            case "session":
                return self._session_lifetime
            case "signing":
                return self._signing_lifetime
            case "master":
                return self._master_lifetime
            case "custody":
                return self._custody_lifetime

    def _generate_key_record(self, key_type: RotationKeyType) -> KeyRecord:
        now = datetime.utcnow()
        lifetime = self._lifetime_for(key_type)
        expires = now + lifetime

        if key_type in ("session", "master", "custody"):
            kem = KyberKEM("ML-KEM-1024")
            kp = kem.generate_keypair()
            kem.close()
            return KeyRecord(
                key_type=key_type,
                algorithm=kp.algorithm,
                fingerprint=kp.fingerprint,
                public_key=kp.public_key,
                secret_key=kp.secret_key,
                created_at=now,
                expires_at=expires,
            )

        # signing
        signer = DilithiumSigner("ML-DSA-87")
        skp = signer.generate_keypair()
        signer.close()
        return KeyRecord(
            key_type=key_type,
            algorithm=skp.algorithm,
            fingerprint=skp.fingerprint,
            public_key=skp.public_key,
            secret_key=skp.secret_key,
            created_at=now,
            expires_at=expires,
        )