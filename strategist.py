# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from dataclasses import asdict, dataclass
from neural_fabric.state import WarLabState


@dataclass
class COA:
    label: str
    confidence: float
    blast_radius: float
    recommended: bool = False


class StrategistNode:
    def run(self, state: WarLabState) -> WarLabState:
        primary = state.get("anomaly_scores", {}).get("primary", 0.0)

        coas = [
            COA("Continue passive monitoring", 0.44, 0.5, recommended=primary < 0.5),
            COA("Isolate affected subsystem", 0.91 if primary > 0.7 else 0.62, 2.0, recommended=primary >= 0.5),
        ]

        state["strategist_coa"] = {
            "coa_options": [asdict(c) for c in coas],
            "recommended_coa": next(c.label for c in coas if c.recommended),
            "nash_posture": "DEFENSIVE_CONTAINMENT" if primary >= 0.5 else "OBSERVE",
            "confidence_score": max(c.confidence for c in coas),
        }
        return state