# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from config.settings import get_settings
from src.master_registry import MasterRegistry

def main() -> None:
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.log_dir.mkdir(parents=True, exist_ok=True)

    registry = MasterRegistry(settings.sqlite_path)
    registry.register_agent("executor-local", "executor", "local://executor")
    registry.register_model(settings.default_model, "ollama", settings.ollama_base_url)
    registry.register_model(settings.fallback_model, "ollama", settings.ollama_base_url)

    print("Bootstrap complete.")

if __name__ == "__main__":
    main()