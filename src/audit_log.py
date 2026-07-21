# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class AuditLogger:
    """Append-only JSONL audit logger with recursive redaction."""

    def __init__(self, audit_dir: Path, redact_field_names: list[str]) -> None:
        self.audit_dir = audit_dir
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.redact_field_names = {name.lower() for name in redact_field_names}
        self.audit_file = self.audit_dir / "audit.jsonl"

    def redact(self, value: Any) -> Any:
        if isinstance(value, dict):
            redacted: dict[str, Any] = {}
            for key, inner_value in value.items():
                if key.lower() in self.redact_field_names:
                    redacted[key] = "***REDACTED***"
                else:
                    redacted[key] = self.redact(inner_value)
            return redacted

        if isinstance(value, list):
            return [self.redact(item) for item in value]

        return value

    def log_event(
        self,
        *,
        actor: str,
        action: str,
        outcome: str,
        risk: str,
        correlation_id: str,
        payload: dict[str, Any] | None = None,
    ) -> str:
        event_id = str(uuid4())
        event = {
            "event_id": event_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "actor": actor,
            "action": action,
            "outcome": outcome,
            "risk": risk,
            "correlation_id": correlation_id,
            "payload": self.redact(payload or {}),
        }
        with self.audit_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "
")
        return event_id