# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CONFIG]

from __future__ import annotations

import os
from typing import Any, Dict, Optional

try:
    import hvac
except Exception:
    hvac = None


class VaultLoader:
    def __init__(self, vault_addr: str, vault_token: str) -> None:
        self.vault_addr = vault_addr
        self.vault_token = vault_token
        self.client = hvac.Client(url=vault_addr, token=vault_token) if hvac and vault_token else None

    def is_ready(self) -> bool:
        return self.client is not None and self.client.is_authenticated()

    def read_secret(self, path: str, mount_point: str = "secret") -> Dict[str, Any]:
        if self.client is None:
            raise RuntimeError("Vault client unavailable or not configured")
        result = self.client.secrets.kv.v2.read_secret_version(path=path, mount_point=mount_point)
        return result["data"]["data"]

    def get_secret_or_env(self, env_name: str, vault_path: Optional[str] = None, key: Optional[str] = None) -> str:
        env_value = os.getenv(env_name)
        if env_value:
            return env_value
        if vault_path and key:
            data = self.read_secret(vault_path)
            if key in data:
                return str(data[key])
        raise KeyError(f"Missing secret for {env_name}")