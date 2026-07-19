# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import psutil
import requests

from config.settings import get_settings
from src.model_manager import ModelManager


def main() -> None:
    settings = get_settings()
    settings.log_dir.mkdir(parents=True, exist_ok=True)

    manager = ModelManager(settings.ollama_base_url, settings.vllm_base_url)
    model_health = manager.health()
    disk = shutil.disk_usage(settings.base_dir if settings.base_dir.exists() else "/")
    memory = psutil.virtual_memory()

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "node_name": settings.node_name,
        "ollama_ok": model_health["ollama"],
        "vllm_ok": model_health["vllm"],
        "sqlite_exists": Path(settings.sqlite_path).exists(),
        "disk_free_gb": round(disk.free / (1024 ** 3), 2),
        "memory_percent": memory.percent,
    }

    logfile = settings.log_dir / "health.log"
    with logfile.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(report) + "
")

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()