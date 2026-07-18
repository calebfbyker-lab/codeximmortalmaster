# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-NEURAL-FABRIC]

from __future__ import annotations

from typing import Iterable

from neural_fabric.state import WarLabState
from neural_fabric.graph import WarLabGraph


class WarLabRunner:
    """
    WarLabRunner:
    - Provides top-level entrypoints for OODA runs.
    - Can be called from your backend APIs or CLI tools.

    Methods:
    - run_ooda(threat_input: str) -> WarLabState
    - run_consensus(threat_input: str) -> dict
    - run_continuous(telemetry_stream: Iterable[str]) -> Iterable[WarLabState]
    """

    def __init__(self) -> None:
        self.graph = WarLabGraph()

    def run_ooda(self, threat_input: str) -> WarLabState:
        """
        Run a single OODA cycle for a given threat input.
        """
        state: WarLabState = {
            "threat_input": threat_input,
            "messages": [],
            "nft_evidence_refs": [],
            "anomaly_scores": {},
            "codex_tag": "CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL",
        }
        state = self.graph.run_once(state)
        return state

    def run_consensus(self, threat_input: str) -> dict:
        """
        Convenience method that returns only the consensus result.
        """
        state = self.run_ooda(threat_input)
        return state.get("consensus", {})

    def run_continuous(self, telemetry_stream: Iterable[str]) -> Iterable[WarLabState]:
        """
        Run continuous OODA cycles on a telemetry stream.
        Yields states for each input.
        """
        for signal in telemetry_stream:
            yield self.run_ooda(signal)


if __name__ == "__main__":
    runner = WarLabRunner()
    example = runner.run_ooda("HNDL exposure on crypto backbone · CRITICAL")
    print("Consensus:", example.get("consensus"))
    print("Messages:")
    for msg in example.get("messages", []):
        print(" -", msg)