# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# PQC provenance: ML-DSA through liboqs-python.
# Intended for development and controlled test environments.

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha3_256
from typing import Literal

import oqs

SignatureAlgorithm = Literal["ML-DSA-65", "ML-DSA-87"]


@dataclass(frozen=True)
class SigningKeyPair:
    algorithm: SignatureAlgorithm
    public_key: bytes
    secret_key: bytes

    @property
    def fingerprint(self) -> str:
        return sha3_256(self.public_key).hexdigest()


@dataclass(frozen=True)
class SignedPayload:
    algorithm: SignatureAlgorithm
    message_digest: str
    signature: bytes
    signer_fingerprint: str


class DilithiumSigner:
    """ML-DSA key lifecycle, signing, and verification wrapper."""

    def __init__(
        self,
        algorithm: SignatureAlgorithm = "ML-DSA-65",
        secret_key: bytes | None = None,
    ) -> None:
        self.algorithm = algorithm
        self._signature = oqs.Signature(algorithm, secret_key)

    def generate_keypair(self) -> SigningKeyPair:
        public_key = self._signature.generate_keypair()
        secret_key = self._signature.export_secret_key()
        return SigningKeyPair(self.algorithm, public_key, secret_key)

    def sign(
        self,
        message: bytes,
        signer_public_key: bytes,
    ) -> SignedPayload:
        signature = self._signature.sign(message)
        return SignedPayload(
            algorithm=self.algorithm,
            message_digest=sha3_256(message).hexdigest(),
            signature=signature,
            signer_fingerprint=sha3_256(signer_public_key).hexdigest(),
        )

    def verify(
        self,
        message: bytes,
        signature: bytes,
        signer_public_key: bytes,
    ) -> bool:
        return self._signature.verify(message, signature, signer_public_key)

    def close(self) -> None:
        self._signature.free()


def canonical_event_bytes(event: dict[str, str]) -> bytes:
    """Create stable bytes for signing a small event record."""
    lines = [f"{key}={event[key]}" for key in sorted(event)]
    return "
".join(lines).encode("utf-8")