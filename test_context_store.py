# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from datetime import datetime, timedelta, timezone

from neural_fabric.memory.context_store import ContextStore
from neural_fabric.memory.schema import GraphKind, MissionContextNode


def test_context_store_filters_active_nodes() -> None:
    store = ContextStore()
    now = datetime.now(timezone.utc)

    active = MissionContextNode(
        id="context:mission-a:1",
        graph=GraphKind.CONTEXT,
        classification="SENSITIVE",
        mission_id="mission-a",
        ooda_cycle=1,
        status="ACTIVE",
        expires_at=(now + timedelta(hours=1)).isoformat(),
    )
    expired = MissionContextNode(
        id="context:mission-a:0",
        graph=GraphKind.CONTEXT,
        classification="SENSITIVE",
        mission_id="mission-a",
        ooda_cycle=0,
        status="STALE",
        expires_at=(now - timedelta(hours=1)).isoformat(),
    )

    store.upsert_node(active)
    store.upsert_node(expired)

    active_nodes = store.get_active_nodes()

    assert len(active_nodes) == 1
    assert active_nodes[0].id == "context:mission-a:1"


def test_context_store_prunes_expired_nodes() -> None:
    store = ContextStore()
    now = datetime.now(timezone.utc)

    node = MissionContextNode(
        id="context:mission-b:0",
        graph=GraphKind.CONTEXT,
        classification="SENSITIVE",
        mission_id="mission-b",
        ooda_cycle=0,
        status="STALE",
        expires_at=(now - timedelta(minutes=5)).isoformat(),
    )
    store.upsert_node(node)

    expired_ids = store.prune_expired()

    assert expired_ids == ["context:mission-b:0"]
    assert store.get_node("context:mission-b:0") is None