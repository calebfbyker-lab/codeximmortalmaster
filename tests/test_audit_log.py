# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

import json

from src.audit_log import AuditLogger


def test_audit_logger_redacts_secret_fields(tmp_path):
    logger = AuditLogger(
        audit_dir=tmp_path / "audit",
        redact_field_names=["secret", "token", "password"],
    )

    logger.log_event(
        actor="tester",
        action="write",
        outcome="ok",
        risk="low",
        correlation_id="corr-1",
        payload={"secret": "abc", "nested": {"token": "xyz", "visible": "yes"}},
    )

    lines = (tmp_path / "audit" / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[0])

    assert record["payload"]["secret"] == "***REDACTED***"
    assert record["payload"]["nested"]["token"] == "***REDACTED***"
    assert record["payload"]["nested"]["visible"] == "yes"