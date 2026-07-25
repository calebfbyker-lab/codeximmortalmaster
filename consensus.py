# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from neural_fabric.state import WarLabState


class ConsensusEngine:
    def evaluate(self, state: WarLabState) -> WarLabState:
        score = state.get("anomaly_scores", {}).get("primary", 0.0)
        if state.get("human_gate_required"):
            mode = "2-of-4 escalate-to-human"
            outcome = "PENDING_HUMAN"
        elif score > 0.5:
            mode = "4-of-4 normal"
            outcome = "APPROVED_CONTAINMENT"
        else:
            mode = "3-of-4 degraded"
            outcome = "APPROVED_MONITORING"

        state["consensus"] = {
            "mode": mode,
            "outcome": outcome,
        }
        return state