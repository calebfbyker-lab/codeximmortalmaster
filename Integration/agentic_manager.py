from __future__ import annotations

from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from integration.subagent_runtime import SubagentRuntime
from integration.task_models import (
    ApprovalRequest,
    ExecutionMode,
    LessonRecord,
    SubTask,
    SubagentRole,
    Task,
    TaskPriority,
    TaskStatus,
)
from integration.training_coordinator import TrainingCoordinator


class AgenticManager:
    def __init__(self) -> None:
        self.tasks: Dict[str, Task] = {}
        self.lessons: Dict[str, LessonRecord] = {}
        self.approvals: Dict[str, ApprovalRequest] = {}
        self.runtime = SubagentRuntime()
        self.training = TrainingCoordinator()

    def add_task(
        self,
        title: str,
        description: str,
        phase: str,
        module: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: List[str] | None = None,
        risk_score: float = 0.0,
        classification: str = "UNCLASSIFIED",
        domain: str = "GENERAL",
    ) -> Task:
        task = Task(
            task_id=f"task-{uuid4().hex[:10]}",
            title=title,
            description=description,
            phase=phase,
            module=module,
            priority=priority,
            dependencies=dependencies or [],
            risk_score=risk_score,
            classification=classification,
            domain=domain,
            human_gate_required=self._requires_human_gate(risk_score, classification, domain),
        )
        if task.human_gate_required:
            task.execution_mode = ExecutionMode.HUMAN_GATE
            task.status = TaskStatus.WAITING_APPROVAL
        else:
            task.status = TaskStatus.READY
        task.recommended_next_action = "Plan subtasks"
        self.tasks[task.task_id] = task
        return task

    def ingest_checklist(self, items: List[str], phase: str = "0", module: str = "bootstrap") -> List[Task]:
        created: List[Task] = []
        for item in items:
            created.append(self.add_task(item, item, phase, module))
        return created

    def plan_subtasks(self, task_id: str) -> Task:
        task = self.tasks[task_id]
        task.subtasks = [
            SubTask(subtask_id=f"sub-{uuid4().hex[:8]}", title=f"Research {task.title}", role=SubagentRole.RESEARCHER),
            SubTask(subtask_id=f"sub-{uuid4().hex[:8]}", title=f"Build {task.title}", role=SubagentRole.BUILDER),
            SubTask(subtask_id=f"sub-{uuid4().hex[:8]}", title=f"Test {task.title}", role=SubagentRole.TESTER),
            SubTask(subtask_id=f"sub-{uuid4().hex[:8]}", title=f"Document {task.title}", role=SubagentRole.DOCUMENTER),
        ]
        task.updated_at = datetime.utcnow()
        task.recommended_next_action = "Spawn subagents"
        return task

    def spawn_for_task(self, task_id: str) -> List[str]:
        task = self.tasks[task_id]
        agent_ids: List[str] = []
        for subtask in task.subtasks:
            agent = self.runtime.spawn_subagent(subtask.role, capabilities=[subtask.role.value.lower()])
            self.runtime.assign_subtask(agent.agent_id, task_id, subtask)
            agent_ids.append(agent.agent_id)
        task.status = TaskStatus.RUNNING
        task.updated_at = datetime.utcnow()
        task.recommended_next_action = "Monitor subagents"
        return agent_ids

    def mark_subtask_complete(self, task_id: str, subtask_id: str) -> None:
        task = self.tasks[task_id]
        for subtask in task.subtasks:
            if subtask.subtask_id == subtask_id:
                subtask.status = TaskStatus.COMPLETED
        if all(st.status == TaskStatus.COMPLETED for st in task.subtasks):
            task.status = TaskStatus.COMPLETED
            task.recommended_next_action = "Archive lesson"
        task.updated_at = datetime.utcnow()

    def request_approval(self, task_id: str, reason: str) -> ApprovalRequest:
        request = ApprovalRequest(request_id=f"apr-{uuid4().hex[:10]}", task_id=task_id, reason=reason)
        self.approvals[request.request_id] = request
        self.tasks[task_id].status = TaskStatus.WAITING_APPROVAL
        self.tasks[task_id].updated_at = datetime.utcnow()
        return request

    def decide_approval(self, request_id: str, operator_id: str, approved: bool) -> ApprovalRequest:
        request = self.approvals[request_id]
        request.status = "APPROVED" if approved else "DENIED"
        request.operator_id = operator_id
        request.decided_at = datetime.utcnow()
        task = self.tasks[request.task_id]
        task.status = TaskStatus.READY if approved else TaskStatus.BLOCKED
        task.updated_at = datetime.utcnow()
        return request

    def record_lesson(self, task_id: str, summary: str, tags: List[str]) -> LessonRecord:
        lesson = LessonRecord(lesson_id=f"lesson-{uuid4().hex[:10]}", task_id=task_id, summary=summary, tags=tags)
        self.lessons[lesson.lesson_id] = lesson
        return lesson

    def start_training_job(self, model_name: str, dataset_ref: str, risk_score: float = 0.0):
        return self.training.create_job(model_name, dataset_ref, risk_score)

    def _requires_human_gate(self, risk_score: float, classification: str, domain: str) -> bool:
        return (
            risk_score > 8.5
            or classification in {"TOP_SECRET", "TS_SCI"}
            or domain in {"BIO", "SPACE", "KINETIC", "RED_TEAM_L5_PLUS"}
        )

    def status_report(self) -> dict:
        return {
            "tasks": [task.model_dump(mode="json") for task in self.tasks.values()],
            "subagents": [agent.model_dump(mode="json") for agent in self.runtime.list_subagents()],
            "training_jobs": [job.model_dump(mode="json") for job in self.training.list_jobs()],
            "approvals": [approval.model_dump(mode="json") for approval in self.approvals.values()],
            "lessons": [lesson.model_dump(mode="json") for lesson in self.lessons.values()],
        }