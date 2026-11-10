# CodexImmortal Master

**A governed multi-agent AI platform — post-quantum cryptography, Byzantine fault-tolerant agent orchestration, sharded distributed storage, and cryptographically attested audit trails.**

This is the engineering monorepo for CodexImmortal: a reference implementation of production-grade agentic AI architecture for defense and enterprise automation. It demonstrates end-to-end systems engineering — cryptographic services, multi-agent coordination, distributed storage, zero-trust deployment, and governed CI/CD.

> **Status:** Active development. All capability modules are tracked in the CodexImmortal CI registry; delivery and certification state is maintained in [`docs/BUILD_CHECKLIST.md`](docs/BUILD_CHECKLIST.md). Registry attestation per module is pending AX-layer certification — treat deployed code as UNCERTIFIED until certified.

---

## What This Repo Demonstrates

- **Post-quantum cryptography in practice** — ML-KEM / ML-DSA signing and encapsulation via liboqs (`pqc_signer_oqs.py`), with environment-tiered algorithms (ML-DSA-65 / ML-KEM-768 in dev, ML-DSA-87 / ML-KEM-1024 in production).
- **Multi-agent orchestration** — four cooperating agents (SENTINEL, STRATEGIST, ARCHIVIST, EXECUTOR) running OODA decision loops under Byzantine fault-tolerant consensus (`consensus.py`).
- **Agent memory as a graph** — persistent knowledge, context, and episodic state on Neo4j (`graph_store.py`, `graph_bridge.py`, `neo4j_query.py`, `context_store.py`).
- **Sharded, tamper-evident storage** — Shamir-split artifacts distributed across IPFS / Arweave / Filecoin with Merkle tamper detection (`storage_mesh/`, `vault_loader.py`).
- **Zero-trust deployment** — Kubernetes with SPIFFE/SPIRE workload identity, HashiCorp Vault secret injection, and default-deny network policies.
- **Local-first AI** — Ollama-hosted inference (llama3.2, 8K context) with no external model dependency.
- **Engineering discipline** — unit-tested core services, staged environment configuration, dockerized full stack.

---

## Architecture

CodexImmortal is organized into five sovereign layers:

| Layer | Responsibility | Representative code |
|---|---|---|
| **PQC Spine** | Post-quantum key lifecycle, signing, validation (FIPS 203/204/205 alignment) | `pqc_signer_oqs.py`, `signer.py`, `validator.py` |
| **Shard Vault** | Shamir-split secret storage across decentralized backends, Merkle tamper detection | `storage_mesh/`, `vault_loader.py`, `sync.py` |
| **MN-NET** | Four-agent mesh (SENTINEL / STRATEGIST / ARCHIVIST / EXECUTOR), OODA loops, BFT consensus | `sentinel.py`, `strategist.py`, `archivist.py`, `executor.py`, `consensus.py`, `graph.py` |
| **NFT Vault** | ERC-721 attestation on Base L2 with ZK-proof references | `schema.py`, `nft_mint.yml` |
| **Playbooks** | Lockdown, sovereign restore, trust purge, federation sync operations | `runner.py`, `node_factory.py`, `policies/` |

Supporting infrastructure: FastAPI gateway (`api_gateway.py`), multi-model persistence (`knowledge_store.py`, `graph_store.py`, `state.py`), and Kubernetes deployment manifests (namespace, ingress, network policies, SPIRE, Vault injector).

## Tech Stack

Python · FastAPI · LangGraph · Neo4j · Ollama (llama3.2) · Docker Compose · Kubernetes · HashiCorp Vault · SPIFFE/SPIRE · liboqs · GitHub Actions

---

## Quickstart

```bash
# 1. Install dependencies
git clone https://github.com/calebfbyker-lab/codeximmortalmaster.git
cd codeximmortalmaster
pip install -r requirements-dev.txt

# 2. Configure environment
cp dev.env .env   # templates only — all secrets injected at runtime via Vault

# 3. Run the full stack
bash bootstrap_warlab.sh      # or: docker compose up -d

# 4. Run the test suite
python -m pytest
```

Local AI inference requires [Ollama](https://ollama.com) with the `llama3.2` model pulled.

---

## Repository Layout

```
codeximmortalmaster/
├── agents/            # MN-NET agent definitions
├── apps/              # application entry points
├── config/            # staged environment configuration
├── dashboard/         # War Lab dashboard surface
├── docs/              # architecture, build checklist, governance
├── neural_fabric/     # inference + agent graph services
├── packages/          # capability module packages
├── policies/          # execution + trust policies
├── scripts/           # operational scripts
├── src/               # core library source
├── storage_mesh/      # shard vault backends
├── tests/             # integration tests
└── *.py               # core services (gateway, agents, stores, PQC)
```

Consolidation of root-level service modules into `packages/` is tracked in the build checklist.

---

## Security

- **No secrets in version control** — committed `*.env` files are templates with blank credentials; production secrets are injected at runtime via HashiCorp Vault.
- **Human-gated operations** — high-impact actions (master shard rotation, doctrine changes, registry renumbering, kinetic/space/OT domains, funding) always require an explicit human approval step.
- **HNDL posture** — post-quantum migration is treated as a harvest-now-decrypt-later defense priority.

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

## Governance and the CI Registry

Every capability is a registered CI module under canonical numbering governed by the AX-03 REGISTRY-SYNC ledger — currently spanning CI-001 through CI-059 plus proposed frontier slots, covering PQC architecture, insider-threat detection, OSINT fusion, model-poisoning defense, cross-mesh federation, and agent memory. Delivery status, human-gate requirements, and the full module matrix live in [`docs/BUILD_CHECKLIST.md`](docs/BUILD_CHECKLIST.md).

> Note: NFT/crypto attestation terminology describes this platform's own design. It does not represent government endorsement, a contract, or authorization.

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Contact

**Caleb Byker** — Founder, CodexImmortal
Web: [codeximmortal.com](https://codeximmortal.com) · GitHub: [@calebfbyker-lab](https://github.com/calebfbyker-lab)

*The War Lab never reaches final form. Evolution = Sovereignty.*
