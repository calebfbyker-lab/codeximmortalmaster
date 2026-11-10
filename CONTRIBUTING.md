# Contributing to CodexImmortal Master

Thanks for your interest. This repository follows a governed, auditable development doctrine — every change is expected to be traceable.

## How to Contribute

1. Fork the repository and create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature
   ```
2. Make your change. Keep commits atomic and use conventional commit messages (`feat:`, `fix:`, `docs:`, `chore:`).
3. Run the test suite before opening a pull request:
   ```bash
   python -m pytest
   ```
4. Open a pull request describing what changed, why, and how it was tested.

## Guidelines

- **Never commit secrets.** Environment files are templates only; use Vault injection at runtime.
- **Preserve module boundaries.** Capability code maps to registered CI modules — reference the module number in your PR description when applicable.
- **Respect human gates.** Changes touching master shard handling, doctrine, registry numbering, or gated domains require explicit maintainer approval.
- **Tests required** for new service modules and security-relevant code paths.

## License

By contributing, you agree that your contributions are licensed under the Apache License 2.0.
