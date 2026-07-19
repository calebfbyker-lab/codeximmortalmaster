# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# Tests PQC KEM round-trip correctness only.

from pqc_utils.kem import KyberKEM


def test_ml_kem_round_trip() -> None:
    receiver = KyberKEM("ML-KEM-768")
    keypair = receiver.generate_keypair()

    sender = KyberKEM("ML-KEM-768")
    encapsulated = sender.encapsulate(keypair.public_key)

    recovered = receiver.decapsulate(encapsulated.ciphertext)

    assert recovered == encapsulated.shared_secret
    assert len(keypair.fingerprint) == 64