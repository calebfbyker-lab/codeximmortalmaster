# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# PQC provenance: ML-KEM through liboqs-python.
# Intended for development and controlled test environments.

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha3_256
from typing import Literal
import os

import oqs

KemAlgorithm = Literal["ML-KEM-768", "ML-KEM-1024"]


@dataclass(frozen=True)
class KemKeyPair:
    algorithm: KemAlgorithm
    public_key: bytes
    secret_key: bytes

    @property
    def fingerprint(self) -> str:
        return sha3_256(self.public_key).hexdigest()


@dataclass(frozen=True)
class KemCiphertext:
    algorithm: KemAlgorithm
    ciphertext: bytes
    shared_secret: bytes


class KyberKEM:
    """Safe lifecycle wrapper around one ML-KEM keypair."""

    def __init__(
        self,
        algorithm: KemAlgorithm = "ML-KEM-768",
        secret_key: bytes | None = None,
    ) -> None:
        self.algorithm = algorithm
        self._kem = oqs.KeyEncapsulation(algorithm, secret_key)

    def generate_keypair(self) -> KemKeyPair:
        public_key = self._kem.generate_keypair()
        secret_key = self._kem.export_secret_key()
        return KemKeyPair(self.algorithm, public_key, secret_key)

    def encapsulate(self, peer_public_key: bytes) -> KemCiphertext:
        ciphertext, shared_secret = self._kem.encap_secret(peer_public_key)
        return KemCiphertext(self.algorithm, ciphertext, shared_secret)

    def decapsulate(self, ciphertext: bytes) -> bytes:
        return self._kem.decap_secret(ciphertext)

    def close(self) -> None:
        self._kem.free()


def derive_session_key(
    pqc_shared_secret: bytes,
    context: bytes,
    key_length: int = 32,
) -> bytes:
    """Derive an application encryption key from an ML-KEM secret."""
    if key_length < 16 or key_length > 64:
        raise ValueError("key_length must be between 16 and 64 bytes")

    salt = os.urandom(32)
    material = b"CODEXIMMORTAL-MLKEM-v1" + salt + context + pqc_shared_secret
    return sha3_256(material).digest()[:key_length]