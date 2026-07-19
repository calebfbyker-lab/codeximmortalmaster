# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# PQC-encrypted message bus for inter-agent communication.

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Dict, List

from .channel import PQCChannel, MessageEnvelope


@dataclass
class PeerInfo:
    peer_id: str
    kem_public_key: bytes
    signing_public_key: bytes


class ReplayDefender:
    """Simple sliding-window replay protection based on seqnum and timestamp."""

    def __init__(self, window: timedelta = timedelta(minutes=5)) -> None:
        self._seen: dict[str, tuple[int, datetime]] = {}
        self._window = window

    def check(self, envelope: MessageEnvelope) -> bool:
        key = f"{envelope.sender_id}"
        now = datetime.utcnow()
        last_seq, last_ts = self._seen.get(key, (0, now - self._window * 2))

        if envelope.seqnum <= last_seq and now - last_ts < self._window:
            return False

        self._seen[key] = (envelope.seqnum, now)
        return True


class MessageBus:
    """Registers peers and delivers PQC-encrypted envelopes."""

    def __init__(self, local_id: str) -> None:
        self.local_id = local_id
        self._channel = PQCChannel(local_id)
        self._peers: Dict[str, PeerInfo] = {}
        self._topics: Dict[str, List[Callable[[bytes], None]]] = defaultdict(list)
        self._replay_defender = ReplayDefender()

    def register_peer(self, peer_id: str, kem_pub: bytes, signing_pub: bytes) -> None:
        self._peers[peer_id] = PeerInfo(peer_id, kem_pub, signing_pub)

    def subscribe(self, topic: str, callback: Callable[[bytes], None]) -> None:
        self._topics[topic].append(callback)

    def initiate_handshake(self, peer_id: str) -> MessageEnvelope:
        peer = self._peers[peer_id]
        kem_ct = self._channel.handshake(peer.kem_public_key)
        # Here you would send kem_ct.ciphertext to the peer over a control channel.
        # For now, return an envelope placeholder.
        return MessageEnvelope(
            sender_id=self.local_id,
            recipient_id=peer_id,
            timestamp=datetime.utcnow().isoformat(),
            nonce=b"",
            seqnum=0,
            ciphertext=kem_ct.ciphertext,
            signature=b"",
            algorithm="SHAKE-256-STREAM",
        )

    def complete_handshake(self, kem_ct: bytes) -> None:
        self._channel.complete_handshake(kem_ct)

    def broadcast(self, topic: str, payload: bytes) -> dict[str, MessageEnvelope]:
        envelopes: dict[str, MessageEnvelope] = {}
        for peer_id, peer in self._peers.items():
            env = self._channel.send(peer_id, payload)
            envelopes[peer_id] = env
        return envelopes

    def deliver(self, envelope: MessageEnvelope) -> None:
        """Process an incoming envelope and call subscribers for its topic."""
        if not self._replay_defender.check(envelope):
            raise ValueError("Replay detected for envelope.")

        peer = self._peers.get(envelope.sender_id)
        if not peer:
            raise ValueError(f"Unknown peer {envelope.sender_id}")

        plaintext = self._channel.receive(envelope, peer.signing_public_key)
        # For Phase 1, treat the topic as a simple prefix in the plaintext.
        topic, _, body = plaintext.partition(b":")
        for cb in self._topics.get(topic.decode("utf-8"), []):
            cb(body)