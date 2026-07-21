# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations

from datetime import datetime, UTC
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_HUMAN_GATE = "awaiting_human_gate"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PolicyAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"


class TaskType(str, Enum):
    CODEGEN = "codegen"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    LINT_FIX = "lint_fix"
    REFACTOR_PLAN = "refactor_plan"
    SYSTEM_CHANGE = "system_change"
    SECRET_OPERATION = "secret_operation"
    EXTERNAL_SYNC = "external_sync"
    DEPLOYMENT = "deployment"
    UNKNOWN = "unknown"


class TaskLineage(BaseModel):
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    parent_task_id: str | None = None
    root_task_id: str | None = None
    depth: int = 0
    child_index: int = 0


class TaskPayload(BaseModel):
    title: str
    summary: str
    task_type: TaskType = TaskType.UNKNOWN
    requested_by: str = "operator"
    content: dict[str, Any] = Field(default_factory=dict)


class TaskRecord(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    payload: TaskPayload
    lineage: TaskLineage = Field(default_factory=TaskLineage)
    status: TaskStatus = TaskStatus.QUEUED
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def mark_running(self) -> None:
        self.status = TaskStatus.RUNNING
        self.started_at = utc_now()

    def mark_completed(self, result: dict[str, Any]) -> None:
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = utc_now()
        self.error = None

    def mark_failed(self, error: str) -> None:
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = utc_now()

    def mark_awaiting_human_gate(self) -> None:
        self.status = TaskStatus.AWAITING_HUMAN_GATE


class PolicyDecision(BaseModel):
    action: PolicyAction
    risk: RiskLevel
    reasons: list[str] = Field(default_factory=list)
    requires_human_gate: bool = False


class SpawnRequest(BaseModel):
    parent_task: TaskRecord
    child_payloads: list[TaskPayload]


class GateDecision(BaseModel):
    approved: bool
    operator_id: str
    justification: str
    decided_at: datetime = Field(default_factory=utc_now)