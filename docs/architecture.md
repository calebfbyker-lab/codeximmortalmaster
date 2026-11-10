# CodexImmortal Master — Target Monorepo Tree

Reference layout for the full War Lab monorepo. The current repository is a partial implementation of this target; delivery status per module is tracked in [`BUILD_CHECKLIST.md`](BUILD_CHECKLIST.md) and [`ENGINEERING_CHECKLIST.md`](ENGINEERING_CHECKLIST.md).

```text
codeximmortal-warlab/
├── README.md
├── LICENSE
├── .gitignore
├── .editorconfig
├── .pre-commit-config.yaml
├── Makefile
├── docker-compose.yml
├── pyproject.toml
├── package.json
├── .env.example
├── warlabcore.py
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── deploy-staging.yml
│       ├── nft-mint.yml
│       └── security-audit.yml
├── docs/
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── sovereign-layers.md
│   │   ├── mn-net.md
│   │   ├── checkpoint-lifecycle.md
│   │   └── threat-model.md
│   ├── doctrine/
│   │   ├── operating-principles.md
│   │   ├── human-gate-policy.md
│   │   ├── classification-policy.md
│   │   └── lineage-policy.md
│   ├── runbooks/
│   │   ├── deployment.md
│   │   ├── key-rotation.md
│   │   ├── shard-recovery.md
│   │   ├── incident-response.md
│   │   └── rollback.md
│   ├── api/
│   │   ├── gateway.md
│   │   ├── threat-board.md
│   │   ├── nft-vault.md
│   │   └── inference.md
│   ├── threat-models/
│   │   ├── prompt-injection.md
│   │   ├── model-poisoning.md
│   │   ├── wallet-drift.md
│   │   └── supply-chain.md
│   └── adr/
│       ├── 0001-monorepo.md
│       ├── 0002-pqc-spine.md
│       ├── 0003-storage-mesh.md
│       └── 0004-checkpoint-attestation.md
├── config/
│   ├── settings.py
│   ├── validator.py
│   ├── vault_loader.py
│   └── profiles/
│       ├── dev.env
│       ├── staging.env
│       ├── production.env
│       └── airgap.env
├── schemas/
│   ├── sovereign_event.schema.json
│   ├── nft_metadata.schema.json
│   ├── training_sample.schema.json
│   ├── training_batch.schema.json
│   ├── checkpoint_manifest.schema.json
│   ├── policy_decision.schema.json
│   ├── playbook.schema.json
│   └── gate_decision.schema.json
├── shared/
│   ├── __init__.py
│   ├── types/
│   ├── models/
│   ├── constants/
│   ├── logging/
│   ├── telemetry/
│   ├── security/
│   └── lineage/
├── pqc-spine/
├── storage-mesh/
├── ai-pipeline/
├── neural-fabric/
├── nft-vault/
├── playbook-engine/
├── threat-board/
├── dashboard/
├── integration/
├── infra/
├── scripts/
├── tests/
└── output/
```

Per-package target trees (pqc-spine, ai-pipeline, neural-fabric, nft-vault, playbook-engine, threat-board, dashboard, integration, infra, scripts, tests) are defined in the original scaffold blueprint.
