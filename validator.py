# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CONFIG]

from __future__ import annotations

from .settings import Settings


def validate_settings(settings: Settings) -> None:
    if settings.shard_threshold > settings.shard_total:
        raise ValueError("shard_threshold cannot exceed shard_total")

    if settings.multisig_threshold < 1:
        raise ValueError("multisig_threshold must be positive")

    if settings.context_window < 2048:
        raise ValueError("context_window too small for MN-NET workloads")

    if settings.auto_escalation_threshold > 10:
        raise ValueError("auto_escalation_threshold must be <= 10")

    if settings.environment == "production" and not settings.nft_contract_address:
        raise ValueError("production requires nft_contract_address")

    if settings.environment == "airgap" and settings.ipfs_pinning_service not in {"local", "offline"}:
        raise ValueError("airgap mode requires local or offline pinning")

    if settings.default_classification in {"TOP_SECRET", "TS_SCI"} and settings.allow_external_persistence_for_ts_sci:
        raise ValueError("TS/SCI external persistence override must remain disabled by default")