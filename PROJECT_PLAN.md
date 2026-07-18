# CodexImmortal Project Plan

CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

## Mission
Build a governed agentic manager that can ingest a project list, decompose work, spawn subagents, coordinate machine-learning training and execution, and connect to the CodexImmortal main monorepo.

## Milestones

| Phase | Module | Outcome | Dependencies | Human Gate |
|---|---|---|---|---|
| 0 | Bootstrap | Repo folders, config, CLI entrypoint | None | No |
| 1 | Task Models | Typed task, milestone, subagent, training job models | Bootstrap | No |
| 2 | Agentic Manager | Backlog ingestion, dependency graph, scheduling, subtask planning | Task Models | No |
| 3 | Subagent Runtime | Spawn, monitor, retire worker agents | Agentic Manager | No |
| 4 | Training Coordinator | Dataset intake, curation, training, evaluation, checkpoint flow | Task Models | No |
| 5 | Governance Layer | Risk scoring, approval queue, human gate controls | Agentic Manager, Training Coordinator | Yes |
| 6 | Dashboard Panel | Task board, subagent board, training queue | Agentic Manager | No |
| 7 | Monorepo Connectors | Bind to PQC, storage, neural, NFT, playbook, threat modules | Governance Layer | Yes |
| 8 | Promotion | Approved production rollout and audit stamp | Monorepo Connectors | Yes |

## Initial Backlog

- [ ] Create typed models for tasks, subtasks, subagents, approvals, lessons, and training jobs.
- [ ] Parse markdown checklist items into structured tasks.
- [ ] Build dependency-aware scheduling.
- [ ] Add subagent spawning with capability-based assignment.
- [ ] Add training workflow for collect, curate, train, evaluate, checkpoint, rollback.
- [ ] Add human gate rules for sensitive tasks.
- [ ] Add CLI commands for list, run, spawn, approve, train, report.
- [ ] Add dashboard panel for operators.
- [ ] Add monorepo connector stubs.
- [ ] Add audit export.

## Human Gate Rules

Trigger approval when any of the following are true:
- Risk score > 8.5
- Domain is BIO, SPACE, KINETIC, or RED_TEAM_L5_PLUS
- Classification is TOP_SECRET or TS_SCI
- Operation touches master shard rotation, model promotion, custody transfer, or autonomous deployment

## Training Workflow

1. Collect task outcomes and lessons.
2. Curate and score samples.
3. Assemble a training batch.
4. Evaluate quality and safety.
5. Request approval for checkpoint promotion when required.
6. Deploy checkpoint or rollback.

## Success Metrics

- Task completion rate
- Mean time to unblock
- Subagent success rate
- Training job pass rate
- Approval turnaround time
- Checkpoint rollback frequency