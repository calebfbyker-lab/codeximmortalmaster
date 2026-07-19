# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# Tests PQC signature validity and tamper rejection.

from pqc_utils.signing import DilithiumSigner, canonical_event_bytes


def test_ml_dsa_sign_and_verify() -> None:
    signer = DilithiumSigner("ML-DSA-65")
    keypair = signer.generate_keypair()

    event = canonical_event_bytes(
        {"event_id": "evt-001", "type": "rotation", "version": "1"}
    )
    signed = signer.sign(event, keypair.public_key)

    assert signer.verify(event, signed.signature, keypair.public_key)
    assert not signer.verify(event + b"-tampered", signed.signature, keypair.public_key)