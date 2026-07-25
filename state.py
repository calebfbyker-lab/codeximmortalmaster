# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class WarLabState(TypedDict, total=False):
    threat_input: str
    sentinel_report: Dict[str, Any]
    strategist_coa: Dict[str, Any]
    archivist_memory: Dict[str, Any]
    executor_plan: Dict[str, Any]
    consensus: Dict[str, Any]
    ooda_loop_count: int
    anomaly_scores: Dict[str, float]
    nft_evidence_refs: List[str]
    human_gate_required: bool
    human_gate_response: Optional[str]
    messages: List[Dict[str, str]]
    codex_tag: str