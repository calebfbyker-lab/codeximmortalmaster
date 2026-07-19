# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations
from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class ModelRoute:
    model_name: str
    backend: str
    endpoint: str


class ModelManager:
    def __init__(self, ollama_url: str, vllm_url: str) -> None:
        self.ollama_url = ollama_url.rstrip("/")
        self.vllm_url = vllm_url.rstrip("/")

    def choose_backend(self, model_name: str) -> ModelRoute:
        if "code" in model_name.lower() or "instruct" in model_name.lower():
            return ModelRoute(model_name=model_name, backend="vllm", endpoint=self.vllm_url)
        return ModelRoute(model_name=model_name, backend="ollama", endpoint=self.ollama_url)

    def health(self) -> dict[str, bool]:
        return {
            "ollama": self._ping(f"{self.ollama_url}/api/tags"),
            "vllm": self._ping(f"{self.vllm_url}/health"),
        }

    def _ping(self, url: str) -> bool:
        try:
            response = requests.get(url, timeout=3)
            return response.status_code < 500
        except requests.RequestException:
            return False