# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

CODEX_TAG = "CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL"


@dataclass(slots=True)
class RouteOption:
    """
    Candidate execution route for a task or mission.

    Fields:
    - confidence: model/agent confidence in the route
    - estimated_latency: time cost (seconds or relative units)
    - blast_radius: expected risk/impact score
    - anomaly_score: SENTINEL anomaly burden attached to this route
    - human_gate_required: whether this route requires human approval
    """

    route_id: str
    confidence: float
    estimated_latency: float
    blast_radius: float
    anomaly_score: float
    human_gate_required: bool = False
    route_score: float = 0.0
    codex_tag: str = CODEX_TAG


class RouteOptimizer:
    """
    Constrained route-ranking engine.

    It prefers:
    - higher confidence,
    - lower latency,
    - lower blast radius,
    - lower anomaly burden,
    - fewer Human Gate blocking points.

    Use this inside the executor/orchestrator before deciding how
    to execute a given war-lab task graph.
    """

    def __init__(
        self,
        latency_weight: float = 1.0,
        blast_weight: float = 1.25,
        anomaly_weight: float = 1.1,
    ) -> None:
        self.latency_weight = latency_weight
        self.blast_weight = blast_weight
        self.anomaly_weight = anomaly_weight

    def score(self, option: RouteOption) -> float:
        """
        Compute a scalar score for a single route option.
        """
        denominator = (
            option.estimated_latency * self.latency_weight
            + option.blast_radius * self.blast_weight
            + max(option.anomaly_score, 0.01) * self.anomaly_weight
            + (2.5 if option.human_gate_required else 0.0)
        )
        return option.confidence / denominator

    def rank(self, options: Iterable[RouteOption]) -> list[RouteOption]:
        """
        Rank a batch of RouteOptions by score (highest first).
        """
        ranked: list[RouteOption] = []
        for option in options:
            option.route_score = self.score(option)
            ranked.append(option)
        ranked.sort(key=lambda item: item.route_score, reverse=True)
        return ranked