# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-NEURAL-FABRIC]

from __future__ import annotations

from typing import TypedDict, Any


class WarLabState(TypedDict, total=False):
    """
    Shared state object passed between MN-NET agents in the War Lab.

    Fields follow the architecture builder specification:
    - threat_input: raw signal
    - sentinel_report: anomaly report structure
    - strategist_coa: course-of-action bundle
    - archivist_memory: memory graph context
    - executor_plan: execution plan object
    - consensus: final consensus record
    - ooda_loop_count: number of OODA cycles run
    - anomaly_scores: per-domain anomaly metrics
    - nft_evidence_refs: minted artifacts backing decisions
    - human_gate_required: whether Human Gate must approve
    - human_gate_response: approval/denial metadata
    - messages: log or trace output
    - codex_tag: provenance label
    """

    threat_input: str
    sentinel_report: dict[str, Any]
    strategist_coa: dict[str, Any]
    archivist_memory: dict[str, Any]
    executor_plan: dict[str, Any]
    consensus: dict[str, Any]
    ooda_loop_count: int
    anomaly_scores: dict[str, float]
    nft_evidence_refs: list[str]
    human_gate_required: bool
    human_gate_response: dict[str, Any]
    messages: list[str]
    codex_tag: str