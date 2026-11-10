# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| `main` | Yes |

## Reporting a Vulnerability

Report vulnerabilities privately to **calebfbyker@gmail.com** with the subject line `[SECURITY] codeximmortalmaster`.

- Please include reproduction steps, affected files, and impact assessment.
- Do not open public issues for suspected vulnerabilities.
- You will receive an acknowledgment within 72 hours.

## Security Posture

- **Secrets:** No credentials are stored in version control. Committed `*.env` files are templates with blank values; runtime secrets are injected via HashiCorp Vault.
- **Cryptography:** Post-quantum algorithms (ML-KEM, ML-DSA per FIPS 203/204) with environment-tiered parameter sets and scheduled key rotation.
- **Human gates:** High-impact operations — master shard rotation, doctrine changes, registry renumbering, kinetic/space/OT domains, and funding decisions — always require explicit human approval.
- **Scope:** This project is a defensive, governance, and simulation platform. It does not provide operational uplift for weapons or offensive attacks on real systems.
