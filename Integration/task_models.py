from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

CODEX_TAG = "CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ExecutionMode(str, Enum):
    AUTOMATED = "AUTOMATED"
    HUMAN_GATE = "HUMAN_GATE"
    AUDIT_STAMP = "AUDIT_STAMP"


class SubagentRole(str, Enum):
    BUILDER = "BUILDER"
    TESTER = "TESTER"
    RESEARCHER = "RESEARCHER"
    TRAINER = "TRAINER"
    EVALUATOR = "EVALUATOR"
    DOCUMENTER = "DOCUMENTER"
    REVIEWER = "REVIEWER"


class TrainingStage(str, Enum):
    COLLECT = "COLLECT"
    CURATE = "CURATE"
    TRAIN = "TRAIN"
    EVALUATE = "EVALUATE"
    CHECKPOINT = "CHECKPOINT"
    ROLLBACK = "ROLLBACK"
    COMPLETE = "COMPLETE"


class LessonRecord(BaseModel):
    lesson_id: str
    task_id: str
    summary: str
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApprovalRequest(BaseModel):
    request_id: str
    task_id: str
    reason: str
    status: str = "PENDING"
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None
    operator_id: Optional[str] = None


class SubTask(BaseModel):
    subtask_id: str
    title: str
    role: SubagentRole
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class Task(BaseModel):
    task_id: str
    title: str
    description: str
    phase: str
    module: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    execution_mode: ExecutionMode = ExecutionMode.AUTOMATED
    owner: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    subtasks: List[SubTask] = Field(default_factory=list)
    risk_score: float = 0.0
    classification: str = "UNCLASSIFIED"
    domain: str = "GENERAL"
    human_gate_required: bool = False
    evidence: Dict[str, str] = Field(default_factory=dict)
    recommended_next_action: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SubagentInstance(BaseModel):
    agent_id: str
    role: SubagentRole
    assigned_task_id: Optional[str] = None
    assigned_subtask_id: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    status: str = "IDLE"
    spawned_at: datetime = Field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)


class TrainingJob(BaseModel):
    job_id: str
    model_name: str
    dataset_ref: str
    stage: TrainingStage = TrainingStage.COLLECT
    status: TaskStatus = TaskStatus.PENDING
    risk_score: float = 0.0
    human_gate_required: bool = False
    metrics: Dict[str, float] = Field(default_factory=dict)
    checkpoint_ref: Optional[str] = None
    rollback_ref: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)