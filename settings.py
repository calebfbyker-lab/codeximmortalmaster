# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CONFIG]

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Literal["dev", "staging", "production", "airgap"] = "dev"
    log_level: str = "INFO"

    pqc_signature_algorithm: str = "ML-DSA-65"
    pqc_kem_algorithm: str = "ML-KEM-768"
    pqc_hash_algorithm: str = "SHA3-256"
    session_key_rotation_hours: int = 24
    signing_key_rotation_days: int = 7
    master_key_rotation_days: int = 30
    nft_custody_rotation_days: int = 90

    shard_total: int = 5
    shard_threshold: int = 3
    shard_replication_factor: int = 3
    ipfs_api_url: str = "http://localhost:5001"
    filecoin_api_url: str = "http://localhost:1234"
    arweave_gateway_url: str = "https://arweave.net"
    cold_storage_path: str = "/var/lib/codex/cold"

    model_name: str = "llama3.2"
    inference_endpoint: str = "http://localhost:11434"
    model_temperature: float = 0.2
    context_window: int = 8192

    base_chain_id: int = 8453
    nft_contract_address: str = ""
    ipfs_pinning_service: str = "local"
    multisig_threshold: int = 3

    human_gate_timeout_seconds: int = 900
    blast_radius_limit: float = 8.5
    auto_escalation_threshold: float = 8.5

    otel_endpoint: str = "http://localhost:4317"
    otel_sampling_rate: float = 1.0

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    redis_url: str = "redis://localhost:6379/0"
    vault_addr: str = "http://127.0.0.1:8200"
    vault_token: str = Field(default="", repr=False)

    allow_external_persistence_for_ts_sci: bool = False
    default_classification: str = "SENSITIVE"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()