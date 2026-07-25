# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from neural_fabric.memory.signer import MockHMACSigner


def test_mock_signer_round_trip() -> None:
    signer = MockHMACSigner(b"super-secret-key", signer_name="unit-test")
    payload = b'{"test":"payload"}'

    envelope = signer.sign(payload)

    assert envelope.algorithm == "HMAC-SHA3-256"
    assert envelope.signer == "unit-test"
    assert signer.verify(payload, envelope) is True


def test_mock_signer_rejects_tampered_payload() -> None:
    signer = MockHMACSigner(b"super-secret-key", signer_name="unit-test")
    payload = b'{"test":"payload"}'
    envelope = signer.sign(payload)

    assert signer.verify(b'{"test":"modified"}', envelope) is False