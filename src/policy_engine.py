# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations

from config.settings import Settings
from src.task_models import PolicyAction, PolicyDecision, RiskLevel, TaskRecord, TaskType


class PolicyEngine:
    """Local-first policy engine for bounded task execution."""

    RECURSIVE_ALLOWED_TYPES = {
        TaskType.CODEGEN,
        TaskType.TESTING,
        TaskType.DOCUMENTATION,
        TaskType.LINT_FIX,
        TaskType.REFACTOR_PLAN,
    }

    ALWAYS_ESCALATE_TYPES = {
        TaskType.SYSTEM_CHANGE,
        TaskType.SECRET_OPERATION,
        TaskType.EXTERNAL_SYNC,
        TaskType.DEPLOYMENT,
    }

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def evaluate(self, task: TaskRecord) -> PolicyDecision:
        reasons: list[str] = []
        content_text = " ".join(
            [
                task.payload.title,
                task.payload.summary,
                " ".join(f"{key}={value}" for key, value in task.payload.content.items()),
            ]
        ).lower()

        if task.lineage.depth > self.settings.max_task_recursion_depth:
            return PolicyDecision(
                action=PolicyAction.DENY,
                risk=RiskLevel.HIGH,
                reasons=["Task recursion depth exceeds configured maximum."],
                requires_human_gate=False,
            )

        if task.payload.task_type in self.ALWAYS_ESCALATE_TYPES:
            return PolicyDecision(
                action=PolicyAction.ESCALATE,
                risk=RiskLevel.HIGH,
                reasons=[f"Task type '{task.payload.task_type.value}' requires human review."],
                requires_human_gate=True,
            )

        matched_keywords = [
            keyword for keyword in self.settings.sensitive_keywords if keyword.lower() in content_text
        ]
        if matched_keywords:
            reasons.append(
                f"Sensitive keywords detected: {', '.join(sorted(set(matched_keywords)))}."
            )
            return PolicyDecision(
                action=PolicyAction.ESCALATE,
                risk=RiskLevel.HIGH,
                reasons=reasons,
                requires_human_gate=True,
            )

        if len(task.payload.summary) > self.settings.max_task_payload_chars:
            return PolicyDecision(
                action=PolicyAction.DENY,
                risk=RiskLevel.MEDIUM,
                reasons=["Task summary exceeds configured payload size limit."],
                requires_human_gate=False,
            )

        if task.payload.task_type == TaskType.UNKNOWN:
            return PolicyDecision(
                action=PolicyAction.ESCALATE,
                risk=RiskLevel.MEDIUM,
                reasons=["Unknown task type requires operator confirmation."],
                requires_human_gate=True,
            )

        return PolicyDecision(
            action=PolicyAction.ALLOW,
            risk=RiskLevel.LOW,
            reasons=["Task is local, bounded, and matches allowlisted development scope."],
            requires_human_gate=False,
        )

    def can_recurse(self, task: TaskRecord) -> PolicyDecision:
        if task.payload.task_type not in self.RECURSIVE_ALLOWED_TYPES:
            return PolicyDecision(
                action=PolicyAction.ESCALATE,
                risk=RiskLevel.MEDIUM,
                reasons=[f"Recursive spawning is not allowed for '{task.payload.task_type.value}'."],
                requires_human_gate=True,
            )

        if task.lineage.depth >= self.settings.max_task_recursion_depth:
            return PolicyDecision(
                action=PolicyAction.DENY,
                risk=RiskLevel.MEDIUM,
                reasons=["Parent task is already at maximum recursion depth."],
                requires_human_gate=False,
            )

        return PolicyDecision(
            action=PolicyAction.ALLOW,
            risk=RiskLevel.LOW,
            reasons=["Task type is eligible for bounded recursive spawning."],
            requires_human_gate=False,
        )