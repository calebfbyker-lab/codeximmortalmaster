# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized configuration for the CodexImmortal private server.

    Environment variables are prefixed with CODEX_ by default, for example:
    - CODEX_ENVIRONMENT=dev
    - CODEX_OLLAMA_BASE_URL=http://127.0.0.1:11434
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CODEX_",
        extra="ignore",
    )

    app_name: str = "codeximmortal-private-server"
    environment: str = "dev"
    node_name: str = "beelink-ser3"

    base_dir: Path = Path("/opt/codeximmortal")
    data_dir: Path = Path("/opt/codeximmortal/data")
    log_dir: Path = Path("/opt/codeximmortal/logs")

    tailscale_hostname: str = "codex-ser3"
    tailscale_tailnet: str = "local.tailnet"

    ollama_base_url: str = "http://127.0.0.1:11434"
    vllm_base_url: str = "http://127.0.0.1:8000"
    default_model: str = "llama3.2"
    fallback_model: str = "mistral"

    sqlite_path: Path = Path("/opt/codeximmortal/data/master_registry.db")
    vector_db_path: Path = Path("/opt/codeximmortal/data/vector_index")

    healthcheck_interval_seconds: int = Field(default=30, ge=5)
    metrics_enabled: bool = True
    log_level: str = "INFO"

    human_gate_required: bool = True
    auto_restart_failed_agents: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached Settings instance so configuration is loaded once.
    """
    return Settings()
# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Local/private runtime settings for governed task execution."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CODEX_",
        extra="ignore",
    )

    app_name: str = "codeximmortal-private-server"
    app_env: str = "development"
    data_dir: Path = Field(default=Path("var/data"))
    audit_dir: Path = Field(default=Path("var/audit"))
    sqlite_path: Path = Field(default=Path("var/data/codex.db"))

    local_only: bool = True
    allow_network_model_calls: bool = False

    max_task_recursion_depth: int = 2
    max_subtasks_per_task: int = 3
    max_task_payload_chars: int = 4000
    max_model_response_chars: int = 12000

    human_gate_timeout_seconds: int = 30
    human_gate_non_interactive_default_deny: bool = True

    sensitive_keywords: list[str] = Field(
        default_factory=lambda: [
            "secret",
            "token",
            "password",
            "api_key",
            "private_key",
            "seed",
            "wallet",
            "mint",
            "deploy",
            "production",
            "shard",
            "master key",
            "classified",
            "bio",
            "space",
            "kinetic",
            "weapons",
            "navigation",
            "cryptokey",
            "firecontrol",
            "commscrypto",
        ]
    )

    redact_field_names: list[str] = Field(
        default_factory=lambda: [
            "password",
            "token",
            "secret",
            "api_key",
            "authorization",
            "private_key",
            "seed",
            "wallet_key",
            "mnemonic",
        ]
    )

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)