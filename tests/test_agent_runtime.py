# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from config.settings import Settings
from src.agent_runtime import AgentRuntime
from src.audit_log import AuditLogger
from src.human_gate import HumanGate
from src.policy_engine import PolicyEngine
from src.subagent_manager import SubagentManager
from src.task_models import TaskPayload, TaskRecord, TaskStatus, TaskType


def build_runtime(tmp_path):
    settings = Settings(
        audit_dir=tmp_path / "audit",
        data_dir=tmp_path / "data",
        human_gate_non_interactive_default_deny=True,
        max_subtasks_per_task=1,
        max_task_recursion_depth=1,
    )
    audit = AuditLogger(settings.audit_dir, settings.redact_field_names)
    policy = PolicyEngine(settings)
    human_gate = HumanGate(settings, audit)
    subagent_manager = SubagentManager(settings, policy, audit)
    return AgentRuntime(settings, audit, policy, human_gate, subagent_manager)


def test_runtime_completes_allowed_task(tmp_path):
    runtime = build_runtime(tmp_path)
    task = TaskRecord(
        payload=TaskPayload(
            title="Write tests",
            summary="Create local unit tests.",
            task_type=TaskType.TESTING,
        )
    )
    runtime.submit_task(task)

    processed = runtime.run(lambda current: {"ok": True, "task_id": current.task_id})

    assert processed[0].status == TaskStatus.COMPLETED


def test_runtime_denies_sensitive_task_via_default_human_gate(tmp_path):
    runtime = build_runtime(tmp_path)
    task = TaskRecord(
        payload=TaskPayload(
            title="Deploy release",
            summary="Prepare production deploy plan.",
            task_type=TaskType.DEPLOYMENT,
        )
    )
    runtime.submit_task(task)

    processed = runtime.run(lambda current: {"ok": True})

    assert processed[0].status == TaskStatus.FAILED
    assert processed[0].error == "Denied by human gate."