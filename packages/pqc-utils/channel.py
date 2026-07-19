# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# Point-to-point PQC channel for agent communication.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from secrets import token_bytes
from typing import Literal

from hashlib import sha3_256

from .kem import KyberKEM, KemCiphertext, derive_session_key
from .signing import DilithiumSigner, SigningKeyPair

CipherAlgorithm = Literal["SHAKE-256-STREAM"]


@dataclass(frozen=True)
class MessageEnvelope:
    sender_id: str
    recipient_id: str
    timestamp: str
    nonce: bytes
    seqnum: int
    ciphertext: bytes
    signature: bytes
    algorithm: CipherAlgorithm


class PQCChannel:
    """Establishes a KEM-backed session key and sends encrypted envelopes."""

    def __init__(
        self,
        local_id: str,
        kem_algorithm: str = "ML-KEM-768",
        signature_algorithm: str = "ML-DSA-65",
    ) -> None:
        self.local_id = local_id
        self._kem = KyberKEM(kem_algorithm)
        self._signer = DilithiumSigner(signature_algorithm)
        self._seqnum = 0

        self._keypair = self._kem.generate_keypair()
        self._signing_keypair = self._signer.generate_keypair()
        self._session_key: bytes | None = None

    @property
    def public_kem_key(self) -> bytes:
        return self._keypair.public_key

    @property
    def public_signing_key(self) -> bytes:
        return self._signing_keypair.public_key

    def handshake(self, peer_public_kem: bytes) -> KemCiphertext:
        """Encapsulate a shared secret to the peer's public key."""
        kem_ct = self._kem.encapsulate(peer_public_kem)
        context = f"{self.local_id}|handshake".encode("utf-8")
        self._session_key = derive_session_key(kem_ct.shared_secret, context)
        return kem_ct

    def complete_handshake(self, kem_ct: bytes) -> None:
        """Decapsulate a received KEM ciphertext and derive a session key."""
        shared = self._kem.decapsulate(kem_ct)
        context = f"{self.local_id}|handshake".encode("utf-8")
        self._session_key = derive_session_key(shared, context)

    def send(self, recipient_id: str, plaintext: bytes) -> MessageEnvelope:
        if self._session_key is None:
            raise RuntimeError("Handshake must be completed before sending messages.")

        nonce = token_bytes(32)
        self._seqnum += 1
        ts = datetime.utcnow().isoformat()

        # Simple XOR stream cipher placeholder; replace with real AEAD.
        keystream = sha3_256(self._session_key + nonce).digest()
        ciphertext = bytes(b ^ keystream[i % len(keystream)] for i, b in enumerate(plaintext))

        to_sign = (
            self.local_id.encode("utf-8")
            + recipient_id.encode("utf-8")
            + ts.encode("utf-8")
            + nonce
            + self._seqnum.to_bytes(8, "big")
            + ciphertext
        )
        signed = self._signer.sign(to_sign, self._signing_keypair.public_key)

        return MessageEnvelope(
            sender_id=self.local_id,
            recipient_id=recipient_id,
            timestamp=ts,
            nonce=nonce,
            seqnum=self._seqnum,
            ciphertext=ciphertext,
            signature=signed.signature,
            algorithm="SHAKE-256-STREAM",
        )

    def receive(self, envelope: MessageEnvelope, peer_public_signing_key: bytes) -> bytes:
        if self._session_key is None:
            raise RuntimeError("Handshake must be completed before receiving messages.")

        to_verify = (
            envelope.sender_id.encode("utf-8")
            + envelope.recipient_id.encode("utf-8")
            + envelope.timestamp.encode("utf-8")
            + envelope.nonce
            + envelope.seqnum.to_bytes(8, "big")
            + envelope.ciphertext
        )

        if not self._signer.verify(to_verify, envelope.signature, peer_public_signing_key):
            raise ValueError("Signature verification failed for incoming envelope.")

        keystream = sha3_256(self._session_key + envelope.nonce).digest()
        plaintext = bytes(
            b ^ keystream[i % len(keystream)] for i, b in enumerate(envelope.ciphertext)
        )
        return plaintext