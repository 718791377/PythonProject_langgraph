## Why

The current mainline memory summary still describes an older memory-refresh handoff as active and does not mention the completed MR 6 readiness review or the later Windows cleanup-output control closeout. Cold-start sessions need the latest published state before choosing any future durable routing smoke or adoption-gate work.

## What Changes

- Refresh the English and Chinese mainline memory summaries for `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`.
- Record the latest landed increments: MR 6 automatic durable routing readiness, Windows cleanup-output control implementation, and the OpenSpec archive for that cleanup-output control.
- State that there are no active OpenSpec changes before this refresh branch and that both local archive worktrees were cleaned.
- Reframe the next active team-mode / durable-state step as a separately reviewed smoke or adoption-gate change only after the target repository, phase, task, and operator consent boundary are named.
- Repair the UTF-8 Chinese companion for `openspec/specs/codex-user-level-mainline-memory-handoff/spec.zh-CN.md`, which had readable intent in the English primary but mojibake in the Chinese companion.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-mainline-memory-handoff`: Clarifies that current mainline memory handoffs must refresh after cleanup-output closeout and durable routing readiness have landed, and must not imply that completed MR 6 work still needs implementation.

## Impact

### Impact Scope

- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - English mainline memory summary refreshed by this change.
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - Chinese companion mainline memory summary refreshed by this change.
- `openspec/specs/codex-user-level-mainline-memory-handoff/spec.zh-CN.md` - Chinese stable-spec companion repaired to readable UTF-8 text.
- `openspec/changes/refresh-mainline-memory-after-cleanup-output-closeout/` - OpenSpec change artifacts for this handoff refresh.

### Explicit Non-Goals

- Do not start a durable team or run live `omx-team-auto.ps1` in this change.
- Do not modify `C:\Users\lenovo\.codex\config.toml`.
- Do not mutate `.omx/state/`, MCP Router database state, user-level skills, Vercel plugin skills, or browser automation skills.
- Do not implement the final personal production-grade persistent Codex CLI team draft as runtime behavior.

### Rollout Sequence

1. Create this OpenSpec change in an isolated feature worktree.
2. Refresh the bilingual mainline memory summaries.
3. Repair the corrupted Chinese stable-spec companion for mainline memory handoff.
4. Validate OpenSpec and repository governance checks.
5. Publish through GitLab-first workflow.

### Rollback Plan

Revert the feature-branch commit before merge, or revert the eventual GitLab merge commit if the refreshed handoff text proves inaccurate.

### Validation Path

- `git diff --check` - verifies whitespace and patch formatting.
- `openspec validate --all` - verifies stable specs and active changes.
- `python tools/check_document_governance_rules.py --root . --json` - verifies bilingual governance document registry rules.
- `python tools/check_implementation_plan_rules.py --root . --json` - verifies implementation-plan registry rules.
- `python tools/check_name_clarity_rules.py --root . --json` - verifies script, path, command, variable, profile, and role names have nearby explanations.
- `python tools/run_openspec_guard.py --root . --tool codex --json` - runs the repository OpenSpec guard bundle.

### Mainline Classification

Existing mainline: `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`.
