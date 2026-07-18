# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable, Mapping, Any

PHI = (1 + sqrt(5)) / 2
CODEX_TAG = "CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL"


@dataclass(slots=True)
class SovereignEventScore:
    """
    Phi-weighted importance score for a single SovereignEvent.
    This object can be attached to threat, task, or mission records.
    """

    event_id: str
    base_score: float
    generation: int
    confidence: float
    blast_radius: float = 1.0
    domain: str = "GENERAL"
    classification: str = "UNCLASS"
    human_gate_required: bool = False
    weighted_score: float = 0.0
    codex_tag: str = CODEX_TAG


@dataclass(slots=True)
class PhiWeightingEngine:
    """
    Doctrine-aware weighting engine.

    - Applies golden-ratio amplification by generation and confidence
    - Divides by blast radius to penalize risky actions
    - Flags Human Gate conditions using War Lab rules
    """

    base_multiplier: float = 1.0
    human_gate_domains: tuple[str, ...] = (
        "KINETIC",
        "BIO",
        "SPACE",
        "WEAPONS",
        "NAVIGATION",
        "CRYPTO_KEY",
        "FIRE_CONTROL",
        "COMMS_CRYPTO",
        "AUTONOMOUS_UAS",
    )
    gated_classifications: tuple[str, ...] = ("TOP_SECRET", "TS_SCI")

    def phi_amplification(self, generation: int, confidence: float) -> float:
        """
        Golden-ratio amplification:
        W(g) = δ_base * (φ^g / 100) * c
        """
        return self.base_multiplier * ((PHI ** generation) / 100.0) * confidence

    def requires_human_gate(self, domain: str, classification: str, score: float) -> bool:
        """
        Human Gate is required if:
        - weighted score > 8.5, OR
        - domain is in the permanent-gate list, OR
        - classification is TOP_SECRET or TS_SCI
        """
        return (
            score > 8.5
            or domain.upper() in self.human_gate_domains
            or classification.upper() in self.gated_classifications
        )

    def score_event(self, event: Mapping[str, Any]) -> SovereignEventScore:
        """
        Score a single event, returning a structured SovereignEventScore.
        """
        base = float(event.get("base_score", 1.0))
        generation = int(event.get("generation", 1))
        confidence = float(event.get("confidence", 0.5))
        blast_radius = max(float(event.get("blast_radius", 1.0)), 1.0)
        domain = str(event.get("domain", "GENERAL")).upper()
        classification = str(event.get("classification", "UNCLASS")).upper()

        weighted = (base * self.phi_amplification(generation, confidence)) / blast_radius
        gate = self.requires_human_gate(domain, classification, weighted)

        return SovereignEventScore(
            event_id=str(event.get("event_id", "unknown")),
            base_score=base,
            generation=generation,
            confidence=confidence,
            blast_radius=blast_radius,
            domain=domain,
            classification=classification,
            human_gate_required=gate,
            weighted_score=weighted,
        )

    def rank_events(self, events: Iterable[Mapping[str, Any]]) -> list[SovereignEventScore]:
        """
        Rank a batch of events by weighted importance (highest first).
        """
        ranked = [self.score_event(event) for event in events]
        ranked.sort(key=lambda item: item.weighted_score, reverse=True)
        return ranked