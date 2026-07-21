# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations

import sys

from config.settings import Settings
from src.audit_log import AuditLogger
from src.task_models import GateDecision, TaskRecord


class HumanGate:
    """Local CLI-only human gate with default deny in non-interactive mode."""

    def __init__(self, settings: Settings, audit_logger: AuditLogger) -> None:
        self.settings = settings
        self.audit_logger = audit_logger

    def request_approval(self, task: TaskRecord) -> GateDecision:
        if self.settings.human_gate_non_interactive_default_deny and not sys.stdin.isatty():
            decision = GateDecision(
                approved=False,
                operator_id="system",
                justification="Denied by default in non-interactive mode.",
            )
            self._audit(task, decision)
            return decision

        prompt = (
            f"
[HUMAN GATE] Approve task {task.task_id}
"
            f"Title: {task.payload.title}
"
            f"Type: {task.payload.task_type.value}
"
            "Approve? [y/N]: "
        )
        raw = input(prompt).strip().lower()
        approved = raw in {"y", "yes"}
        justification = "Approved by local operator." if approved else "Denied by local operator."
        operator_id = "local-operator"
        decision = GateDecision(
            approved=approved,
            operator_id=operator_id,
            justification=justification,
        )
        self._audit(task, decision)
        return decision

    def _audit(self, task: TaskRecord, decision: GateDecision) -> None:
        self.audit_logger.log_event(
            actor=decision.operator_id,
            action="human_gate_decision",
            outcome="approved" if decision.approved else "denied",
            risk="high",
            correlation_id=task.lineage.correlation_id,
            payload={
                "task_id": task.task_id,
                "title": task.payload.title,
                "justification": decision.justification,
            },
        )