# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from neural_fabric.consensus import ConsensusEngine
from neural_fabric.nodes.archivist import ArchivistNode
from neural_fabric.nodes.executor import ExecutorNode
from neural_fabric.nodes.sentinel import SentinelNode
from neural_fabric.nodes.strategist import StrategistNode
from neural_fabric.state import WarLabState


class WarLabGraph:
    def __init__(self, sentinel: SentinelNode, strategist: StrategistNode, archivist: ArchivistNode, executor: ExecutorNode, consensus: ConsensusEngine) -> None:
        self.sentinel = sentinel
        self.strategist = strategist
        self.archivist = archivist
        self.executor = executor
        self.consensus = consensus

    def invoke(self, state: WarLabState) -> WarLabState:
        state = self.sentinel.run(state)
        state = self.strategist.run(state)
        state = self.archivist.run(state)
        state = self.executor.run(state)
        state = self.consensus.evaluate(state)
        return state


def build_war_lab_graph(sentinel: SentinelNode, strategist: StrategistNode, archivist: ArchivistNode, executor: ExecutorNode, consensus: ConsensusEngine) -> WarLabGraph:
    return WarLabGraph(sentinel, strategist, archivist, executor, consensus)