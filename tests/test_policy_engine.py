# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from config.settings import Settings
from src.policy_engine import PolicyEngine
from src.task_models import PolicyAction, TaskLineage, TaskPayload, TaskRecord, TaskType


def test_policy_allows_low_risk_codegen_task(tmp_path):
    settings = Settings(audit_dir=tmp_path / "audit", data_dir=tmp_path / "data")
    engine = PolicyEngine(settings)
    task = TaskRecord(
        payload=TaskPayload(
            title="Generate local tests",
            summary="Create unit tests for a local module.",
            task_type=TaskType.CODEGEN,
        )
    )

    decision = engine.evaluate(task)

    assert decision.action == PolicyAction.ALLOW


def test_policy_escalates_sensitive_keyword(tmp_path):
    settings = Settings(audit_dir=tmp_path / "audit", data_dir=tmp_path / "data")
    engine = PolicyEngine(settings)
    task = TaskRecord(
        payload=TaskPayload(
            title="Handle wallet migration",
            summary="Prepare wallet key export plan.",
            task_type=TaskType.DOCUMENTATION,
        )
    )

    decision = engine.evaluate(task)

    assert decision.action == PolicyAction.ESCALATE
    assert decision.requires_human_gate is True


def test_policy_denies_excess_depth(tmp_path):
    settings = Settings(
        audit_dir=tmp_path / "audit",
        data_dir=tmp_path / "data",
        max_task_recursion_depth=1,
    )
    engine = PolicyEngine(settings)
    task = TaskRecord(
        payload=TaskPayload(
            title="Nested child",
            summary="Too deep.",
            task_type=TaskType.CODEGEN,
        ),
        lineage=TaskLineage(depth=2),
    )

    decision = engine.evaluate(task)

    assert decision.action == PolicyAction.DENY