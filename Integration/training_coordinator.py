from __future__ import annotations

from datetime import datetime
from typing import Dict
from uuid import uuid4

from integration.task_models import TrainingJob, TaskStatus, TrainingStage


class TrainingCoordinator:
    def __init__(self) -> None:
        self.jobs: Dict[str, TrainingJob] = {}

    def create_job(self, model_name: str, dataset_ref: str, risk_score: float = 0.0) -> TrainingJob:
        job = TrainingJob(
            job_id=f"train-{uuid4().hex[:10]}",
            model_name=model_name,
            dataset_ref=dataset_ref,
            risk_score=risk_score,
            human_gate_required=risk_score > 8.5,
        )
        self.jobs[job.job_id] = job
        return job

    def advance_stage(self, job_id: str, stage: TrainingStage) -> TrainingJob:
        job = self.jobs[job_id]
        job.stage = stage
        job.status = TaskStatus.RUNNING if stage != TrainingStage.COMPLETE else TaskStatus.COMPLETED
        job.updated_at = datetime.utcnow()
        return job

    def record_metrics(self, job_id: str, metrics: Dict[str, float]) -> TrainingJob:
        job = self.jobs[job_id]
        job.metrics.update(metrics)
        job.updated_at = datetime.utcnow()
        return job

    def checkpoint(self, job_id: str, checkpoint_ref: str) -> TrainingJob:
        job = self.jobs[job_id]
        job.stage = TrainingStage.CHECKPOINT
        job.checkpoint_ref = checkpoint_ref
        job.updated_at = datetime.utcnow()
        return job

    def rollback(self, job_id: str, rollback_ref: str) -> TrainingJob:
        job = self.jobs[job_id]
        job.stage = TrainingStage.ROLLBACK
        job.rollback_ref = rollback_ref
        job.status = TaskStatus.FAILED
        job.updated_at = datetime.utcnow()
        return job

    def list_jobs(self) -> list[TrainingJob]:
        return list(self.jobs.values())