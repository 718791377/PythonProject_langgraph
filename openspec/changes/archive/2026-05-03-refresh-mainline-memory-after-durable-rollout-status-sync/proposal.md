## Why

The current mainline memory summary still presents the MCP scope refresh as the latest handoff, but the repository has since landed and archived the Codex direct browser/design MCP policy and the durable rollout status-sync work. Cold-start sessions need the latest published state so they do not reopen MR 5 durable-state work or stale MCP-scope follow-up tasks.

## What Changes

- Refresh the English and Chinese mainline memory summaries for `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`.
- Record the latest landed increments: Codex direct browser/design MCP policy, durable rollout plan status sync, Chinese status-text repair, and archive closeout.
- Update publication and active-change handoff text to reflect `main` / `gitlab/main` / `github/main` at `b822343` at the start of this refresh branch.
- Reframe safe next actions around MR 6 readiness or separately named future changes, not already completed MR 5 work.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-mainline-memory-handoff`: Clarifies that mainline memory handoffs should be refreshed after durable rollout status-sync archive work lands, especially when a prior implementation plan no longer points at the real next slice.

## Impact

### Impact Scope

- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - English mainline memory summary refreshed by this change.
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - Chinese companion mainline memory summary refreshed by this change.
- `openspec/changes/refresh-mainline-memory-after-durable-rollout-status-sync/` - OpenSpec change artifacts for this handoff refresh.

### Explicit Non-Goals

- Do not modify user-level skills, Vercel plugin skills, browser automation skills, or `C:\Users\lenovo\.codex\config.toml`.
- Do not mutate `.omx/state/`, MCP Router database state, or user-level MCP configuration.
- Do not implement MR 6 automatic durable routing in this change.
- Do not archive this change while another active session owns broad `openspec/specs` scope; archive must be serialized after that ownership clears.

### Rollout Sequence

1. Create this OpenSpec change in an isolated feature worktree.
2. Refresh the bilingual mainline memory summaries.
3. Validate OpenSpec and repository governance checks.
4. Publish through GitLab-first workflow.
5. Archive later in a serialized archive worktree when stable-spec ownership is clear.

### Rollback Plan

Revert the feature-branch commit before merge, or revert the eventual GitLab merge commit if the refreshed handoff text proves inaccurate.

### Validation Path

- `git diff --check` - verifies whitespace and patch formatting.
- `openspec validate --all` - verifies stable specs and active changes.
- `python tools/check_document_governance_rules.py --root . --json` - verifies bilingual governance document registry rules.
- `python tools/check_implementation_plan_rules.py --root . --json` - verifies implementation-plan registry rules.
- `python tools/run_openspec_guard.py --root . --json` - runs the repository OpenSpec guard bundle.

### Mainline Classification

Existing mainline: `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`.
