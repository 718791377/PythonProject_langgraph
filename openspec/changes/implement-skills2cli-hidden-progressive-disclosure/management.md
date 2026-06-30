# Management Record

## Open

- [x] Value: hidden skills remain usable without increasing default model-visible pressure.
- [x] Success criteria: hidden search/load works for `grill-me` and `stop-slop` alias, usage events are recorded, recommendations are generated, apply is manual-only and receipt-backed.
- [x] Constraints: no plugin cache edits, no `config.toml` edits, no remote publication.

## Design

- [x] Delivery tailoring: two local integration packages, Phase A plan-freeze and Phase B runtime.
- [x] Risks: accidental global restore, noisy alias matches, unsafe auto-apply, daily guard bypass.
- [x] Acceptance evidence path: `test/skills2cli.test.py`, OpenSpec guard, local gate, local MR review.

## Build

- [x] Execution mode selected: worktree-isolated local-main-first implementation.
- [x] Quality evidence recorded before local `main` integration: Phase A uses implementation-plan rules, OpenSpec strict validation, worktree receipt checker, precommit update/archive review, and OpenSpec guard before local integration.
- [x] Blocker decision recorded: native verifier review was used read-only; durable runtime team is not required for Phase A because this package is plan-freeze only, while Phase B remains multi-slice implementation.

## Verify

- [ ] Variance review completed.
- [ ] Risk/change impact reviewed.
- [ ] Control decision: continue to archive when runtime validation passes.

## Archive

- [ ] Stable spec promoted.
- [ ] Lessons/receipt recorded.
- [ ] Archive evidence recorded.

## Monitoring

- [x] Current facts: plan frozen from user-selected defaults on 2026-06-30.
- [x] Return/no-return decision: continue; no earlier-phase rework needed.
