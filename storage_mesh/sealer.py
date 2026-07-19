# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_256
from os import urandom

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from .classifier import AssetProfile


@dataclass(frozen=True)
class SealedPayload:
    asset_id: str
    ciphertext: bytes
    nonce: bytes
    created_at: str
    expires_at: str | None
    profile: AssetProfile
    wrapped_deks: dict[str, bytes]


class PayloadSealer:
    """Seal bytes with AEAD; PQC KEM wrapping is injected by a key service."""

    def seal(
        self,
        data: bytes,
        profile: AssetProfile,
        recipient_public_keys: dict[str, bytes],
        dek_wrapper: callable,
        expires_at: str | None = None,
    ) -> SealedPayload:
        dek = ChaCha20Poly1305.generate_key()
        nonce = urandom(12)
        asset_id = sha3_256(data).hexdigest()

        aad = (
            f"{asset_id}|{profile.sensitivity}|{profile.storage_ring}"
        ).encode()
        ciphertext = ChaCha20Poly1305(dek).encrypt(nonce, data, aad)

        wrapped_deks = {
            recipient_id: dek_wrapper(public_key, dek)
            for recipient_id, public_key in recipient_public_keys.items()
        }

        return SealedPayload(
            asset_id=asset_id,
            ciphertext=ciphertext,
            nonce=nonce,
            created_at=datetime.now(timezone.utc).isoformat(),
            expires_at=expires_at,
            profile=profile,
            wrapped_deks=wrapped_deks,
        )

    def unseal(
        self,
        sealed: SealedPayload,
        recipient_id: str,
        dek_unwrapper: callable,
    ) -> bytes:
        wrapped_dek = sealed.wrapped_deks[recipient_id]
        dek = dek_unwrapper(wrapped_dek)

        aad = (
            f"{sealed.asset_id}|{sealed.profile.sensitivity}|"
            f"{sealed.profile.storage_ring}"
        ).encode()
        return ChaCha20Poly1305(dek).decrypt(sealed.nonce, sealed.ciphertext, aad)