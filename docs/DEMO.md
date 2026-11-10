# Offline demo and CI

Status: standalone deterministic simulation, UNCERTIFIED. No new CI identifier. Existing runtime, CI, deployment, and registry files are not modified.

This CI-ready revision embeds synthetic fixtures in codex_demo.core.scenario rather than requiring the earlier ZIP's examples/events files. It does not invoke neural_fabric or claim to test the existing runtime.

## Run from repository root

Python 3.11 or 3.12; standard library only, no pip install or credentials.

```bash
python -m unittest discover -s tests_offline -v
python -m codex_demo run --scenario routine > routine-receipt.json
python -m codex_demo verify routine-receipt.json
python -m codex_demo run --scenario human_gate
python -m codex_demo run --scenario tampered
```

Exit codes: 0 = simulation complete or receipt integrity matches; 3 = expected human-gate hold; 2 = rejected or invalid input. All receipts have executed=false. No approval override is implemented.

Custom synthetic envelopes may be supplied with run --input FILE (64 KiB maximum). Use envelope(event) to compute the fixture digest. Unknown fields, invalid ranges, nonfinite scores, unknown categories, and hash mismatches are rejected. Never submit actual classified data; classification labels are synthetic test metadata only.

## Flow and policy

SENTINEL fixture score -> STRATEGIST deterministic recommendation -> POLICY gate -> EXECUTOR simulation/hold -> ARCHIVIST JSON receipt. These are role-simulation trace stages, not autonomous agents or LLM inference.

Review recommendation threshold: anomaly >= 0.7. Gate independently on Shield impact > 8.5, KINETIC/BIO/SPACE/OT/ICS domains, TOP_SECRET/TS_SCI labels, and master-shard/registry/doctrine/funding/multi-theater operations. Scores are synthetic inputs, not measured impact or detection accuracy.

## GitHub Actions

.github/workflows/offline-demo.yml runs on push, pull_request, or manual dispatch. It tests Python 3.11 and 3.12 without installing runtime dependencies, asserts expected CLI exit codes, verifies routine and held receipts, and uploads logs/receipts for 14 days. Test failures propagate; none are suppressed. This does not configure branch protection or make the job a required merge check; an administrator must enable that separately.

A green demo check validates only this isolated simulation. Existing CI may still fail independently. Workflow runs require GitHub-hosted runners and action downloads; offline describes the demo's execution, not provisioning the CI runner.

SHA-256 checks integrity relative to the supplied digest, not authenticity: an editor can change data and recompute the hash. There are no signatures, PQC, BFT, NFTs, live scanning, external-service calls, or actual execution. The CLI reads local input and prints JSON; shell redirection and CI artifact upload write the outputs.
