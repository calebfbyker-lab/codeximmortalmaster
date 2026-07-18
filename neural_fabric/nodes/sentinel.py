# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-NEURAL-FABRIC]

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from neural_fabric.state import WarLabState


@dataclass(slots=True)
class AnomalyReport:
    """
    Structured anomaly report.

    score: overall anomaly score (0.0 - 1.0)
    domain_scores: per-domain scores (supply chain, insider, HNDL, etc.)
    escalation_level: NONE / INFO / WARN / CRITICAL
    evidence_package: minimal evidence bundle (hashes, ids)
    """

    score: float
    domain_scores: Mapping[str, float]
    escalation_level: str
    evidence_package: Mapping[str, Any]


class SentinelNode:
    """
    SENTINEL:
    - Ingests threat_input and telemetry.
    - Produces anomaly scores and escalation level.
    - Integrates later with storage-mesh tamper detection and wallet activity.

    This is the Observe phase of OODA.
    """

    def run(self, state: WarLabState) -> WarLabState:
        raw = state.get("threat_input", "")

        # Simple placeholder scoring logic; extend with real models later.
        base_score = 0.0
        if "HNDL" in raw.upper():
            base_score = 0.7
        elif "CRITICAL" in raw.upper():
            base_score = 0.8
        elif raw:
            base_score = 0.4

        domain_scores = {
            "supply_chain": 0.3,
            "insider": 0.2,
            "hndl": base_score,
            "model_poisoning": 0.1,
            "wallet_drift": 0.15,
        }

        if base_score >= 0.8:
            level = "CRITICAL"
        elif base_score >= 0.5:
            level = "WARN"
        elif base_score > 0.0:
            level = "INFO"
        else:
            level = "NONE"

        report = AnomalyReport(
            score=base_score,
            domain_scores=domain_scores,
            escalation_level=level,
            evidence_package={"signal_hash": f"hash:{len(raw)}"},
        )

        state["sentinel_report"] = {
            "score": report.score,
            "domain_scores": dict(report.domain_scores),
            "escalation_level": report.escalation_level,
            "evidence_package": dict(report.evidence_package),
        }
        state["anomaly_scores"] = dict(report.domain_scores)
        state.setdefault("messages", []).append(
            f"SENTINEL: anomaly_score={report.score}, escalation={report.escalation_level}"
        )
        state["codex_tag"] = "CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL"
        return state