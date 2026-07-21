# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations

from config.settings import Settings
from src.audit_log import AuditLogger
from src.policy_engine import PolicyEngine
from src.task_models import TaskLineage, TaskPayload, TaskRecord


class SubagentManager:
    """Creates bounded child tasks for safe local recursive execution."""

    def __init__(
        self,
        settings: Settings,
        policy_engine: PolicyEngine,
        audit_logger: AuditLogger,
    ) -> None:
        self.settings = settings
        self.policy_engine = policy_engine
        self.audit_logger = audit_logger

    def spawn_children(self, parent: TaskRecord, child_payloads: list[TaskPayload]) -> list[TaskRecord]:
        recurse_decision = self.policy_engine.can_recurse(parent)
        if recurse_decision.action != recurse_decision.action.ALLOW:
            self.audit_logger.log_event(
                actor="subagent_manager",
                action="spawn_children",
                outcome=recurse_decision.action.value,
                risk=recurse_decision.risk.value,
                correlation_id=parent.lineage.correlation_id,
                payload={
                    "parent_task_id": parent.task_id,
                    "reasons": recurse_decision.reasons,
                },
            )
            return []

        limited_payloads = child_payloads[: self.settings.max_subtasks_per_task]
        children: list[TaskRecord] = []
        root_task_id = parent.lineage.root_task_id or parent.task_id

        for index, payload in enumerate(limited_payloads, start=1):
            child = TaskRecord(
                payload=payload,
                lineage=TaskLineage(
                    correlation_id=parent.lineage.correlation_id,
                    parent_task_id=parent.task_id,
                    root_task_id=root_task_id,
                    depth=parent.lineage.depth + 1,
                    child_index=index,
                ),
            )
            children.append(child)
            self.audit_logger.log_event(
                actor="subagent_manager",
                action="child_task_spawned",
                outcome="created",
                risk="low",
                correlation_id=child.lineage.correlation_id,
                payload={
                    "parent_task_id": parent.task_id,
                    "child_task_id": child.task_id,
                    "child_index": index,
                    "depth": child.lineage.depth,
                    "task_type": child.payload.task_type.value,
                    "title": child.payload.title,
                },
            )

        return children

    def plan_from_parent(self, parent: TaskRecord) -> list[TaskPayload]:
        """Deterministic development-only decomposition stub."""
        summary = parent.payload.summary.lower()
        planned: list[TaskPayload] = []

        if parent.payload.task_type.value == "codegen":
            planned.append(
                TaskPayload(
                    title=f"{parent.payload.title} - implementation slice",
                    summary="Implement the primary code path for the requested local feature.",
                    task_type=parent.payload.task_type,
                    requested_by="subagent_manager",
                )
            )
            planned.append(
                TaskPayload(
                    title=f"{parent.payload.title} - tests",
                    summary="Create or update unit tests for the feature behavior.",
                    task_type="testing",
                    requested_by="subagent_manager",
                )
            )

        if "documentation" in summary or parent.payload.task_type.value == "documentation":
            planned.append(
                TaskPayload(
                    title=f"{parent.payload.title} - docs",
                    summary="Update local README and usage notes for the task result.",
                    task_type="documentation",
                    requested_by="subagent_manager",
                )
            )

        return planned[: self.settings.max_subtasks_per_task]