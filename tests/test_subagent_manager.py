# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from config.settings import Settings
from src.audit_log import AuditLogger
from src.policy_engine import PolicyEngine
from src.subagent_manager import SubagentManager
from src.task_models import TaskPayload, TaskRecord, TaskType


def build_manager(tmp_path):
    settings = Settings(
        audit_dir=tmp_path / "audit",
        data_dir=tmp_path / "data",
        max_subtasks_per_task=2,
        max_task_recursion_depth=2,
    )
    audit = AuditLogger(settings.audit_dir, settings.redact_field_names)
    policy = PolicyEngine(settings)
    return settings, SubagentManager(settings, policy, audit)


def test_spawn_children_respects_cap(tmp_path):
    _, manager = build_manager(tmp_path)
    parent = TaskRecord(
        payload=TaskPayload(
            title="Parent codegen",
            summary="Build local feature and tests.",
            task_type=TaskType.CODEGEN,
        )
    )
    payloads = [
        TaskPayload(title="one", summary="a", task_type=TaskType.CODEGEN),
        TaskPayload(title="two", summary="b", task_type=TaskType.TESTING),
        TaskPayload(title="three", summary="c", task_type=TaskType.DOCUMENTATION),
    ]

    children = manager.spawn_children(parent, payloads)

    assert len(children) == 2
    assert all(child.lineage.parent_task_id == parent.task_id for child in children)


def test_plan_from_parent_creates_deterministic_children(tmp_path):
    _, manager = build_manager(tmp_path)
    parent = TaskRecord(
        payload=TaskPayload(
            title="Feature work",
            summary="Create implementation and documentation.",
            task_type=TaskType.CODEGEN,
        )
    )

    planned = manager.plan_from_parent(parent)

    assert len(planned) >= 2