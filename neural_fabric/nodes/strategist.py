# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-NEURAL-FABRIC]

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

from neural_fabric.state import WarLabState


@dataclass(slots=True)
class PayoffMatrix:
    """
    Simplified payoff matrix for COA selection.

    rows: COA options
    columns: outcomes or adversary moves
    values: numeric payoffs (utility)
    """

    rows: List[str]
    columns: List[str]
    values: List[List[float]]


@dataclass(slots=True)
class StrategistOutput:
    coa_options: List[str]
    recommended_coa: str
    nash_posture: str
    confidence_score: float
    payoff_matrix: PayoffMatrix


class StrategistNode:
    """
    STRATEGIST:
    - Uses anomaly report + threat_input.
    - Generates a small set of COA options.
    - Picks a recommended COA with a Nash-style posture label.
    """

    def run(self, state: WarLabState) -> WarLabState:
        sentinel = state.get("sentinel_report", {})
        base_score = float(sentinel.get("score", 0.0))

        # Example COAs; in the full system these would be derived from MITRE mappings.
        coa_options = ["MONITOR", "LOCKDOWN", "TRUST_PURGE"]
        if base_score >= 0.7:
            recommended = "LOCKDOWN"
            posture = "DEFENSIVE_MAX"
            conf = 0.9
        elif base_score >= 0.4:
            recommended = "MONITOR"
            posture = "CAUTIOUS"
            conf = 0.75
        else:
            recommended = "MONITOR"
            posture = "NORMAL"
            conf = 0.6

        payoff = PayoffMatrix(
            rows=coa_options,
            columns=["ADVERSARY_ADVANCE", "ADVERSARY_RETREAT"],
            values=[
                [0.4, 0.6],  # MONITOR
                [0.8, 0.7],  # LOCKDOWN
                [0.7, 0.5],  # TRUST_PURGE
            ],
        )

        out = StrategistOutput(
            coa_options=coa_options,
            recommended_coa=recommended,
            nash_posture=posture,
            confidence_score=conf,
            payoff_matrix=payoff,
        )

        state["strategist_coa"] = {
            "options": out.coa_options,
            "recommended": out.recommended_coa,
            "posture": out.nash_posture,
            "confidence": out.confidence_score,
            "payoff_matrix": {
                "rows": payoff.rows,
                "columns": payoff.columns,
                "values": payoff.values,
            },
        }
        state.setdefault("messages", []).append(
            f"STRATEGIST: recommended={out.recommended_coa}, posture={out.nash_posture}, conf={out.confidence_score}"
        )
        return state