# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping

from agents.sovereign_agent import SovereignAgent, SovereignTask, ExecutionDecision
from neural_fabric.runner import WarLabRunner


@dataclass(slots=True)
class OrchestratorLogEntry:
    """
    Proof log entry for orchestrated actions.

    Fields:
    - task_id: identifier for the task
    - agent_type: SOVEREIGN / MN-NET / HYBRID
    - decision: execution mode or consensus decision
    - phi_score: importance score from SovereignAgent
    - consensus_mode: 4-of-4 / 3-of-4 / 2-of-4
    - escalate_to_human: whether commander approval is required
    """

    task_id: str
    agent_type: str
    decision: str
    phi_score: float
    consensus_mode: str
    escalate_to_human: bool


class AgentOrchestrator:
    """
    AgentOrchestrator:
    - Manages a fleet of agents (SovereignAgent + MN-NET fabric).
    - Dispatches tasks in a round-robin or policy-based manner.
    - Produces proof logs for later NFT minting and audit.

    The Module-File-Algorithms-Status table describes:
    - 7-agent fleet
    - round-robin dispatch
    - proof log
    This scaffold gives you the core behavior to build on.
    """

    def __init__(self) -> None:
        self.sovereign_agent = SovereignAgent()
        self.neural_runner = WarLabRunner()
        self._counter = 0
        self._proof_log: List[OrchestratorLogEntry] = []

    # =========
    # Dispatch
    # =========

    def _next_agent_type(self) -> str:
        """
        Simple round-robin across three agent types:
        - SOVEREIGN only
        - MN-NET only
        - HYBRID (use both)
        You can expand this to 7 typed agents later.
        """
        types = ["SOVEREIGN", "MN-NET", "HYBRID"]
        agent_type = types[self._counter % len(types)]
        self._counter += 1
        return agent_type

    def dispatch(self, task_payload: Any, metadata: Mapping[str, Any]) -> dict[str, Any]:
        """
        Main entrypoint: orchestrate a single task.

        1. Wrap payload/metadata into a SovereignTask.
        2. Choose agent_type via round-robin.
        3. Run SovereignAgent DECIDE/ACT if applicable.
        4. Run MN-NET OODA/consensus if applicable.
        5. Combine results, create proof log entry, and return summary.
        """
        task = SovereignTask(
            task_id=str(metadata.get("task_id", f"task-{self._counter}")),
            payload=task_payload,
            metadata=metadata,
        )

        agent_type = self._next_agent_type()

        # SovereignAgent path
        decision: ExecutionDecision | None = None
        sovereign_plan: dict[str, Any] | None = None
        if agent_type in ("SOVEREIGN", "HYBRID"):
            decision = self.sovereign_agent.decide(task)
            sovereign_plan = self.sovereign_agent.act(decision)

        # MN-NET path
        consensus: Mapping[str, Any] | None = None
        if agent_type in ("MN-NET", "HYBRID"):
            threat_input = str(task_payload)
            consensus = self.neural_runner.run_consensus(threat_input)

        # Build proof log entry
        phi_score = decision.phi_score if decision else 0.0
        consensus_mode = str(consensus.get("mode", "N/A")) if consensus else "N/A"
        escalate = bool(consensus.get("escalate_to_human", False)) if consensus else (
            decision.human_gate_required if decision else False
        )

        log_entry = OrchestratorLogEntry(
            task_id=task.task_id,
            agent_type=agent_type,
            decision=(
                consensus.get("decision", decision.mode if decision else "UNKNOWN")
                if consensus
                else (decision.mode if decision else "UNKNOWN")
            ),
            phi_score=phi_score,
            consensus_mode=consensus_mode,
            escalate_to_human=escalate,
        )
        self._proof_log.append(log_entry)

        # Combined summary for API/dashboard
        result = {
            "task_id": task.task_id,
            "agent_type": agent_type,
            "sovereign_decision": {
                "mode": decision.mode if decision else None,
                "phi_score": phi_score,
                "human_gate_required": decision.human_gate_required if decision else None,
                "plan": sovereign_plan,
            },
            "mnnet_consensus": consensus,
            "proof_log_entry": {
                "task_id": log_entry.task_id,
                "agent_type": log_entry.agent_type,
                "decision": log_entry.decision,
                "phi_score": log_entry.phi_score,
                "consensus_mode": log_entry.consensus_mode,
                "escalate_to_human": log_entry.escalate_to_human,
            },
        }
        return result

    # =========
    # Introspection
    # =========

    @property
    def proof_log(self) -> List[OrchestratorLogEntry]:
        """
        Access the orchestrator proof log (for NFT minting or audit).
        """
        return list(self._proof_log)


if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    meta = {
        "task_id": "evt-001",
        "severity": 125.1,
        "generation": 9,
        "confidence": 0.92,
        "blast_radius": 2.0,
        "domain": "GENERAL",
        "classification": "UNCLASS",
    }
    out = orchestrator.dispatch("HNDL exposure on crypto backbone · CRITICAL", meta)
    print("Dispatch result:", out)