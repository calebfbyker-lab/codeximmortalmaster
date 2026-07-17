#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from integration.agentic_manager import AgenticManager
from integration.task_models import TaskPriority, TrainingStage


def build_demo_manager() -> AgenticManager:
    manager = AgenticManager()
    task = manager.add_task(
        title="Connect evolution proposal to monorepo",
        description="Create integration package, service registry, and manager hooks",
        phase="7",
        module="integration",
        priority=TaskPriority.HIGH,
        risk_score=4.2,
    )
    manager.plan_subtasks(task.task_id)
    manager.spawn_for_task(task.task_id)
    job = manager.start_training_job("strategist-prime-lora", "dataset://lessons/codex")
    manager.training.advance_stage(job.job_id, TrainingStage.CURATE)
    manager.training.advance_stage(job.job_id, TrainingStage.TRAIN)
    manager.training.record_metrics(job.job_id, {"loss": 0.18, "eval_score": 0.91})
    return manager


def main() -> None:
    parser = argparse.ArgumentParser(description="CodexImmortal agentic manager CLI")
    parser.add_argument("command", choices=["demo-report"], help="Command to run")
    args = parser.parse_args()

    manager = build_demo_manager()

    if args.command == "demo-report":
        print(json.dumps(manager.status_report(), indent=2, default=str))


if __name__ == "__main__":
    main()