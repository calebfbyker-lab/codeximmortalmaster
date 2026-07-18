# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Literal

from agents.phi_weighting import PhiWeightingEngine, SovereignEventScore
from agents.route_optimizer import RouteOption, RouteOptimizer
from agents.growth_scheduler import GrowthScheduler, GrowthCheckpoint


AgentPhase = Literal["OBSERVE", "ORIENT", "DECIDE", "ACT", "LEARN"]
ExecutionMode = Literal["AUTOMATED", "HUMAN_GATE", "AUDIT_STAMP"]


@dataclass(slots=True)
class SovereignTask:
    """
    High-level task object that the SovereignAgent can process.

    Fields:
    - task_id: unique identifier
    - payload: raw input (threat signal, mission order, code fault, etc.)
    - metadata: domain, classification, blast_radius, severity, etc.
    """

    task_id: str
    payload: Any
    metadata: Mapping[str, Any]


@dataclass(slots=True)
class ExecutionDecision:
    """
    Result of the DECIDE phase.

    Fields:
    - task_id: original task id
    - chosen_route: best RouteOption selected
    - mode: AUTOMATED / HUMAN_GATE / AUDIT_STAMP
    - phi_score: phi-weighted importance for this task
    - human_gate_required: whether Human Gate must approve
    """

    task_id: str
    chosen_route: RouteOption | None
    mode: ExecutionMode
    phi_score: float
    human_gate_required: bool
    checkpoint: GrowthCheckpoint | None


class SovereignAgent:
    """
    SovereignAgent: the War Lab's primary runtime agent.

    Responsibilities:
    - Ingest tasks and normalize them into SovereignEvents.
    - Apply phi weighting to compute importance and Human Gate flags.
    - Build candidate routes and rank them using RouteOptimizer.
    - Emit an ExecutionDecision for the orchestrator and executor.
    - Track evolution checkpoints via GrowthScheduler.

    This class is designed to be called by agents/agent_orchestrator.py.
    """

    def __init__(self) -> None:
        self.phi_engine = PhiWeightingEngine()
        self.route_optimizer = RouteOptimizer()
        self.growth_scheduler = GrowthScheduler()
        self._evolution_step = 0

    # =========
    # OBSERVE
    # =========

    def observe(self, task: SovereignTask) -> SovereignEventScore:
        """
        Map a SovereignTask into an event and score it.

        Required metadata keys (with defaults if missing):
        - base_score
        - generation
        - confidence
        - blast_radius
        - domain
        - classification
        """
        meta = task.metadata
        event = {
            "event_id": task.task_id,
            "base_score": meta.get("base_score", meta.get("severity", 1.0)),
            "generation": meta.get("generation", 9),
            "confidence": meta.get("confidence", 0.75),
            "blast_radius": meta.get("blast_radius", 1.0),
            "domain": meta.get("domain", "GENERAL"),
            "classification": meta.get("classification", "UNCLASS"),
        }
        return self.phi_engine.score_event(event)

    # =========
    # ORIENT
    # =========

    def orient(self, score: SovereignEventScore) -> list[RouteOption]:
        """
        Build a small set of candidate routes based on the event score.

        In a real system this would use:
        - STRATEGIST COA options
        - SENTINEL anomaly scores
        - ARCHIVIST precedents

        Here we provide a simple scaffold that the orchestrator can extend.
        """
        base_conf = score.confidence
        base_blast = score.blast_radius

        options: list[RouteOption] = [
            RouteOption(
                route_id=f"{score.event_id}-route-A",
                confidence=base_conf,
                estimated_latency=1.0,
                blast_radius=base_blast,
                anomaly_score=0.2,
                human_gate_required=score.human_gate_required,
            ),
            RouteOption(
                route_id=f"{score.event_id}-route-B",
                confidence=max(base_conf - 0.05, 0.0),
                estimated_latency=0.8,
                blast_radius=base_blast + 0.5,
                anomaly_score=0.4,
                human_gate_required=score.human_gate_required,
            ),
        ]
        return options

    # =========
    # DECIDE
    # =========

    def decide(self, task: SovereignTask) -> ExecutionDecision:
        """
        Run Observe → Orient → Decide for a single task and return
        a structured ExecutionDecision for the orchestrator.
        """
        self._evolution_step += 1

        # Observe: score event
        event_score = self.observe(task)

        # Orient: build and rank routes
        candidate_routes = self.orient(event_score)
        ranked_routes = self.route_optimizer.rank(candidate_routes)
        chosen_route = ranked_routes[0] if ranked_routes else None

        # Mode selection based on Human Gate and phi score
        if event_score.human_gate_required:
            mode: ExecutionMode = "HUMAN_GATE"
        elif event_score.weighted_score > 5.0:
            mode = "AUTOMATED"
        else:
            mode = "AUDIT_STAMP"

        checkpoint = self.growth_scheduler.checkpoint(self._evolution_step)

        return ExecutionDecision(
            task_id=task.task_id,
            chosen_route=chosen_route,
            mode=mode,
            phi_score=event_score.weighted_score,
            human_gate_required=event_score.human_gate_required,
            checkpoint=checkpoint,
        )

    # =========
    # ACT + LEARN
    # =========

    def act(self, decision: ExecutionDecision) -> dict[str, Any]:
        """
        Placeholder Act phase: return a structured plan for the executor.

        In the full War Lab:
        - EXECUTOR would use this to build an execution plan.
        - NFT vault and playbook engine would mint audit artifacts.
        """
        return {
            "task_id": decision.task_id,
            "route_id": decision.chosen_route.route_id if decision.chosen_route else None,
            "mode": decision.mode,
            "phi_score": decision.phi_score,
            "human_gate_required": decision.human_gate_required,
            "checkpoint_step": decision.checkpoint.step if decision.checkpoint else None,
            "checkpoint_threshold": decision.checkpoint.promote_threshold
            if decision.checkpoint
            else None,
        }

    def learn(self, tasks: Iterable[SovereignTask]) -> list[ExecutionDecision]:
        """
        Batch-processing helper: run DECIDE across multiple tasks
        and return the decisions. This can be used for simulations
        or continuous telemetry streams.
        """
        decisions: list[ExecutionDecision] = []
        for task in tasks:
            decisions.append(self.decide(task))
        return decisions