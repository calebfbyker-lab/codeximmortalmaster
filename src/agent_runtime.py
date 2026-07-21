# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations

import json
import sqlite3
import time


class AgentRuntime:
    """
    Minimal runtime loop that pulls queued tasks and marks them completed.

    This is intentionally simple: the actual inference call will be added later.
    """

    def __init__(self, db_path: str, poll_interval: int = 5) -> None:
        self.db_path = db_path
        self.poll_interval = poll_interval

    def run_once(self) -> None:
        """
        Fetch a single queued task and mark it as running -> completed.
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT task_id, payload
                FROM tasks
                WHERE status = 'queued'
                ORDER BY created_at ASC
                LIMIT 1
                """
            ).fetchone()

            if not row:
                return

            task_id, payload = row
            _ = json.loads(payload)  # placeholder where actual inference will go

            conn.execute(
                "UPDATE tasks SET status = 'running' WHERE task_id = ?",
                (task_id,),
            )
            conn.execute(
                "UPDATE tasks SET status = 'completed' WHERE task_id = ?",
                (task_id,),
            )

    def run_forever(self) -> None:
        """
        Continuously poll for tasks. Use systemd or a supervisor to manage this.
        """
        while True:
            self.run_once()
            time.sleep(self.poll_interval)
# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations

from collections import deque
from typing import Callable

from config.settings import Settings
from src.audit_log import AuditLogger
from src.human_gate import HumanGate
from src.policy_engine import PolicyEngine
from src.subagent_manager import SubagentManager
from src.task_models import PolicyAction, TaskRecord, TaskStatus


class AgentRuntime:
    """Governed local runtime for bounded recursive task execution."""

    def __init__(
        self,
        settings: Settings,
        audit_logger: AuditLogger,
        policy_engine: PolicyEngine,
        human_gate: HumanGate,
        subagent_manager: SubagentManager,
    ) -> None:
        self.settings = settings
        self.audit_logger = audit_logger
        self.policy_engine = policy_engine
        self.human_gate = human_gate
        self.subagent_manager = subagent_manager
        self.queue: deque[TaskRecord] = deque()

    def submit_task(self, task: TaskRecord) -> None:
        self.queue.append(task)
        self.audit_logger.log_event(
            actor=task.payload.requested_by,
            action="task_submitted",
            outcome=task.status.value,
            risk="low",
            correlation_id=task.lineage.correlation_id,
            payload={
                "task_id": task.task_id,
                "title": task.payload.title,
                "task_type": task.payload.task_type.value,
                "depth": task.lineage.depth,
            },
        )

    def run(self, executor: Callable[[TaskRecord], dict]) -> list[TaskRecord]:
        processed: list[TaskRecord] = []

        while self.queue:
            task = self.queue.popleft()
            decision = self.policy_engine.evaluate(task)

            self.audit_logger.log_event(
                actor="policy_engine",
                action="task_evaluated",
                outcome=decision.action.value,
                risk=decision.risk.value,
                correlation_id=task.lineage.correlation_id,
                payload={
                    "task_id": task.task_id,
                    "reasons": decision.reasons,
                },
            )

            if decision.action == PolicyAction.DENY:
                task.mark_failed("Denied by policy engine.")
                processed.append(task)
                continue

            if decision.action == PolicyAction.ESCALATE:
                task.mark_awaiting_human_gate()
                gate = self.human_gate.request_approval(task)
                if not gate.approved:
                    task.mark_failed("Denied by human gate.")
                    processed.append(task)
                    continue

            task.mark_running()
            self.audit_logger.log_event(
                actor="agent_runtime",
                action="task_started",
                outcome=TaskStatus.RUNNING.value,
                risk=decision.risk.value,
                correlation_id=task.lineage.correlation_id,
                payload={"task_id": task.task_id},
            )

            try:
                result = executor(task)
                task.mark_completed(result)

                self.audit_logger.log_event(
                    actor="agent_runtime",
                    action="task_completed",
                    outcome=TaskStatus.COMPLETED.value,
                    risk=decision.risk.value,
                    correlation_id=task.lineage.correlation_id,
                    payload={
                        "task_id": task.task_id,
                        "result_keys": sorted(result.keys()),
                    },
                )

                planned_children = self.subagent_manager.plan_from_parent(task)
                children = self.subagent_manager.spawn_children(task, planned_children)
                for child in children:
                    self.submit_task(child)

            except Exception as exc:  # noqa: BLE001
                task.mark_failed(str(exc))
                self.audit_logger.log_event(
                    actor="agent_runtime",
                    action="task_failed",
                    outcome=TaskStatus.FAILED.value,
                    risk=decision.risk.value,
                    correlation_id=task.lineage.correlation_id,
                    payload={
                        "task_id": task.task_id,
                        "error": str(exc),
                    },
                )

            processed.append(task)

        return processed