# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

import base64
import hashlib
import hmac
from dataclasses import dataclass
from typing import Protocol


class SignerError(Exception):
    pass


@dataclass
class SignatureEnvelope:
    algorithm: str
    signer: str
    signature: str

    def to_dict(self) -> dict:
        return {
            "algorithm": self.algorithm,
            "signer": self.signer,
            "signature": self.signature,
        }


class SnapshotSigner(Protocol):
    def sign(self, payload: bytes) -> SignatureEnvelope:
        ...

    def verify(self, payload: bytes, envelope: SignatureEnvelope) -> bool:
        ...


class MockHMACSigner:
    def __init__(self, secret_key: bytes, signer_name: str = "mock-hmac-signer") -> None:
        self.secret_key = secret_key
        self.signer_name = signer_name
        self.algorithm = "HMAC-SHA3-256"

    def sign(self, payload: bytes) -> SignatureEnvelope:
        digest = hmac.new(self.secret_key, payload, hashlib.sha3_256).digest()
        return SignatureEnvelope(
            algorithm=self.algorithm,
            signer=self.signer_name,
            signature=base64.b64encode(digest).decode("utf-8"),
        )

    def verify(self, payload: bytes, envelope: SignatureEnvelope) -> bool:
        if envelope.algorithm != self.algorithm:
            return False
        expected = self.sign(payload)
        return hmac.compare_digest(expected.signature, envelope.signature)


class MLDSASigner:
    """
    Adapter interface for a future ML-DSA implementation from oqs-python or pqc-spine.

    Replace `_sign_impl` and `_verify_impl` with the actual library calls once the
    PQC runtime is available in the CodexImmortal environment.
    """

    def __init__(self, private_key: bytes, public_key: bytes, signer_name: str = "mldsa-signer") -> None:
        self.private_key = private_key
        self.public_key = public_key
        self.signer_name = signer_name
        self.algorithm = "ML-DSA-FIPS-204"

    def sign(self, payload: bytes) -> SignatureEnvelope:
        signature = self._sign_impl(payload)
        return SignatureEnvelope(
            algorithm=self.algorithm,
            signer=self.signer_name,
            signature=base64.b64encode(signature).decode("utf-8"),
        )

    def verify(self, payload: bytes, envelope: SignatureEnvelope) -> bool:
        if envelope.algorithm != self.algorithm:
            return False
        try:
            raw_signature = base64.b64decode(envelope.signature.encode("utf-8"))
        except Exception as exc:
            raise SignerError("Invalid base64 signature") from exc
        return self._verify_impl(payload, raw_signature)

    def _sign_impl(self, payload: bytes) -> bytes:
        raise NotImplementedError(
            "Wire this method to the PQC provider, for example oqs.Signature('ML-DSA-65').sign(payload)."
        )

    def _verify_impl(self, payload: bytes, signature: bytes) -> bool:
        raise NotImplementedError(
            "Wire this method to the PQC provider, for example oqs.Signature('ML-DSA-65').verify(payload, signature, public_key)."
        )