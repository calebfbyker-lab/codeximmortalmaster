# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

import base64
from dataclasses import dataclass

from .signer import SignatureEnvelope, SignerError

try:
    import oqs
except Exception as exc:
    oqs = None
    _oqs_import_error = exc
else:
    _oqs_import_error = None


@dataclass
class MLDSAKeypair:
    algorithm: str
    public_key: bytes
    secret_key: bytes


class OQSMLDSASigner:
    def __init__(self, secret_key: bytes, public_key: bytes, algorithm: str = "ML-DSA-65", signer_name: str = "archivist-mldsa") -> None:
        if oqs is None:
            raise RuntimeError(f"oqs-python unavailable: {_oqs_import_error}")
        self.secret_key = secret_key
        self.public_key = public_key
        self.algorithm = algorithm
        self.signer_name = signer_name

    @classmethod
    def generate(cls, algorithm: str = "ML-DSA-65", signer_name: str = "archivist-mldsa") -> tuple["OQSMLDSASigner", MLDSAKeypair]:
        if oqs is None:
            raise RuntimeError(f"oqs-python unavailable: {_oqs_import_error}")
        with oqs.Signature(algorithm) as signer:
            public_key = signer.generate_keypair()
            secret_key = signer.export_secret_key()
        instance = cls(secret_key=secret_key, public_key=public_key, algorithm=algorithm, signer_name=signer_name)
        keypair = MLDSAKeypair(algorithm=algorithm, public_key=public_key, secret_key=secret_key)
        return instance, keypair

    def sign(self, payload: bytes) -> SignatureEnvelope:
        with oqs.Signature(self.algorithm, secret_key=self.secret_key) as signer:
            raw_signature = signer.sign(payload)
        return SignatureEnvelope(
            algorithm=self.algorithm,
            signer=self.signer_name,
            signature=base64.b64encode(raw_signature).decode("utf-8"),
        )

    def verify(self, payload: bytes, envelope: SignatureEnvelope) -> bool:
        if envelope.algorithm != self.algorithm:
            return False
        try:
            raw_signature = base64.b64decode(envelope.signature.encode("utf-8"))
        except Exception as exc:
            raise SignerError("Invalid base64 signature") from exc
        with oqs.Signature(self.algorithm) as verifier:
            return verifier.verify(payload, raw_signature, self.public_key)