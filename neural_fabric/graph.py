# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-NEURAL-FABRIC]

from __future__ import annotations

from typing import Callable

from neural_fabric.state import WarLabState
from neural_fabric.nodes.sentinel import SentinelNode
from neural_fabric.nodes.strategist import StrategistNode
from neural_fabric.nodes.archivist import ArchivistNode
from neural_fabric.nodes.executor import ExecutorNode
from neural_fabric.consensus import ConsensusEngine


class WarLabGraph:
    """
    Minimal neural-fabric graph for OODA:

      SENTINEL  -> STRATEGIST -> ARCHIVIST -> EXECUTOR -> CONSENSUS

    In a full LangGraph implementation, this would be a StateGraph with
    conditional edges. Here we provide a simple Python pipeline.
    """

    def __init__(self) -> None:
        self.sentinel = SentinelNode()
        self.strategist = StrategistNode()
        self.archivist = ArchivistNode()
        self.executor = ExecutorNode()
        self.consensus = ConsensusEngine()

    def run_once(self, state: WarLabState) -> WarLabState:
        """
        Run a single OODA cycle across all nodes.
        """
        state.setdefault("ooda_loop_count", 0)
        state["ooda_loop_count"] += 1

        state = self.sentinel.run(state)
        state = self.strategist.run(state)
        state = self.archivist.run(state)
        state = self.executor.run(state)
        state = self.consensus.run(state)

        return state

    def run_until(self, state: WarLabState, predicate: Callable[[WarLabState], bool]) -> WarLabState:
        """
        Run multiple OODA cycles until predicate(state) is True.
        """
        while not predicate(state):
            state = self.run_once(state)
        return state