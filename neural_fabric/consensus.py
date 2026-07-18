# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-NEURAL-FABRIC]

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from neural_fabric.state import WarLabState


@dataclass(slots=True)
class ConsensusResult:
    """
    Consensus result across SENTINEL, STRATEGIST, ARCHIVIST, EXECUTOR.

    mode: 4-of-4 / 3-of-4 / 2-of-4
    decision: primary recommended COA or plan mode
    escalate_to_human: whether to escalate to commander
    veto_reason: optional veto reason
    """

    mode: str
    decision: str
    escalate_to_human: bool
    veto_reason: str | None


class ConsensusEngine:
    """
    ConsensusEngine:
    - Implements 4-of-4 / 3-of-4 / 2-of-4 voting rules.
    - Uses anomaly and posture to decide escalation.
    """

    def run(self, state: WarLabState) -> WarLabState:
        sentinel = state.get("sentinel_report", {})
        strategist = state.get("strategist_coa", {})
        executor = state.get("executor_plan", {})

        score = float(sentinel.get("score", 0.0))
        posture = strategist.get("posture", "NORMAL")
        mode = executor.get("mode", "AUDIT_STAMP")

        votes: Mapping[str, bool] = {
            "sentinel": score >= 0.4,
            "strategist": posture in ("CAUTIOUS", "DEFENSIVE_MAX"),
            "archivist": True,  # archivist typically does not veto
            "executor": mode in ("AUTOMATED", "HUMAN_GATE"),
        }

        yes_count = sum(1 for v in votes.values() if v)
        if yes_count == 4:
            consensus_mode = "4-of-4"
        elif yes_count == 3:
            consensus_mode = "3-of-4"
        else:
            consensus_mode = "2-of-4"

        escalate_to_human = consensus_mode == "2-of-4" or mode == "HUMAN_GATE"
        veto_reason = None
        if consensus_mode == "2-of-4":
            veto_reason = "Low agent agreement; escalate to commander."

        result = ConsensusResult(
            mode=consensus_mode,
            decision=strategist.get("recommended", "MONITOR"),
            escalate_to_human=escalate_to_human,
            veto_reason=veto_reason,
        )

        state["consensus"] = {
            "mode": result.mode,
            "decision": result.decision,
            "escalate_to_human": result.escalate_to_human,
            "veto_reason": result.veto_reason,
        }
        state.setdefault("messages", []).append(
            f"CONSENSUS: mode={result.mode}, decision={result.decision}, escalate={result.escalate_to_human}"
        )
        return state