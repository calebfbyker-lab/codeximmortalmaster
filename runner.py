# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from neural_fabric.consensus import ConsensusEngine
from neural_fabric.graph import build_war_lab_graph
from neural_fabric.memory.archivist_service import ArchivistService
from neural_fabric.nodes.archivist import ArchivistNode
from neural_fabric.nodes.executor import ExecutorNode
from neural_fabric.nodes.sentinel import SentinelNode
from neural_fabric.nodes.strategist import StrategistNode
from neural_fabric.state import WarLabState


class WarLabRunner:
    def __init__(self, archivist_service: ArchivistService) -> None:
        self.graph = build_war_lab_graph(
            sentinel=SentinelNode(),
            strategist=StrategistNode(),
            archivist=ArchivistNode(archivist_service),
            executor=ExecutorNode(),
            consensus=ConsensusEngine(),
        )

    def run_ooda(self, threat_input: str) -> WarLabState:
        state: WarLabState = {
            "threat_input": threat_input,
            "ooda_loop_count": 1,
            "messages": [{"role": "system", "content": "OODA cycle initialized"}],
            "codex_tag": "[CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]",
        }
        return self.graph.invoke(state)

    def run_consensus(self, question: str) -> dict:
        result = self.run_ooda(question)
        return result.get("consensus", {})

    async def run_continuous(self, telemetry_stream):
        for idx, event in enumerate(telemetry_stream, start=1):
            state: WarLabState = {
                "threat_input": str(event),
                "ooda_loop_count": idx,
                "messages": [{"role": "system", "content": "Continuous OODA cycle"}],
                "codex_tag": "[CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]",
            }
            yield self.graph.invoke(state)