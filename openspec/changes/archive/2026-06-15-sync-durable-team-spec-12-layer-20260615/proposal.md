## Why

The durable-team documentation family has been refreshed across lifecycle, white paper, research, MRD, North Star, plan, and playbook documents, but the stable durable-team OpenSpec requirement still centers its title and Chinese companion on a legacy ten-layer landing-map framing. The active goal also needs an explicit corpus-sync checkpoint so later maintainers can distinguish current tracked evidence from missing ignored extraction artifacts and avoid over-claiming that every related file was refreshed in one batch.

## What Changes

- Reframe the stable `codex-cli-personal-production-durable-team-plan` requirement around the 10-to-12-layer bridge, corpus-sync evidence, and draft-only runtime boundary.
- Add a small durable-team corpus sync checkpoint to the core document family: plan, playbook, white paper, MRD, North Star, and research note.
- Record that the June 2026 fresh-source evidence is tracked through reports/archive/docs, while raw extraction caches remain ignored and may not be present in the current worktree.
- Add verification artifacts for this bounded documentation/spec synchronization slice.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-cli-personal-production-durable-team-plan`: clarify that the draft plan requirement covers the 10-layer runtime capability core, the current 12-layer product/business lifecycle target, the core durable-team corpus sync checkpoint, and the no-runtime-evidence boundary.

## Impact

- Affected documentation: core durable-team plan/playbook/whitepaper/MRD/North Star/research docs and the stable/delta OpenSpec spec for `codex-cli-personal-production-durable-team-plan`.
- No runtime code, user-level launcher, native subagent, `native_omx`, LangGraph, model-provider, or remote-publication behavior changes.

## Governance Fields

- `impact_scope`: docs-only stable-spec and core durable-team corpus synchronization.
- `explicit_non_goals`: no fresh extraction rerun, no claim that ignored raw extraction artifacts exist in the current worktree, no runtime persistent-team launch, no remote publication, no merge of white paper and research note.
- `rollout_sequence`: update OpenSpec artifacts; update stable/delta spec language; add corpus checkpoints; run OpenSpec and document checks; commit on the isolated branch.
- `rollback_plan`: revert this branch commit or restore the touched documentation/spec files from `main`.
- `validation_path`: `openspec validate sync-durable-team-spec-12-layer-20260615 --strict --json`, `openspec validate --all`, document pair/mojibake/name checks, precommit archive/update review, and local gate if this slice is promoted to local main.
- `mainline_classification`: existing durable-team documentation governance mainline, under the long-term `codex_cli_personal_production_durable_team` objective.
