## Why

The current mainline memory summary still foregrounds the earlier official-update replay increment even though the latest merged repository state now includes the task ownership precheck checker. This can mislead cold-start sessions into reopening completed work or missing the latest checker-backed write-safety boundary.

This change refreshes the mainline handoff so new sessions can start from the real current state: no active OpenSpec changes, task ownership precheck landed, and the next work should be selected deliberately.

## What Changes

- Update the current mainline memory summary to record that the task ownership precheck checker has landed and been archived.
- Add a reusable requirement for current mainline memory handoffs to identify the latest landed governance or checker increment before listing next actions.
- Keep the repository startup summary stable; this change only updates drift-prone mainline memory details.
- Keep this as a documentation and handoff update only; no runtime behavior changes are introduced.

## Capabilities

### New Capabilities
- `codex-user-level-mainline-memory-handoff`: defines how current mainline memory summaries record latest landed increments, active-change state, and safe next-action choices for cold-start sessions.

### Modified Capabilities
- None.

## Impact

Impact scope:
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - English current-mainline memory handoff.
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - Chinese current-mainline memory handoff.
- `openspec/changes/refresh-mainline-memory-after-task-ownership-precheck/` - OpenSpec change artifacts for this documentation-only update.

Explicit non-goals:
- Do not change `tools/check_session_ownership_claims.py` behavior.
- Do not modify `tools/codex-official-update-patch-replay-template.ps1` runtime behavior.
- Do not start a durable team.
- Do not change GitLab/GitHub publication policy.
- Do not modify consumer projects; this change is limited to the current repository's documentation and OpenSpec artifacts.

Rollout sequence:
1. Create this OpenSpec change and its bilingual artifacts.
2. Update the current mainline memory summary pair.
3. Validate OpenSpec and repository governance checkers.
4. Commit to a feature branch and use the GitLab-first publication workflow if the user asks to publish.

Rollback plan:
- Revert this feature branch before merge if the handoff wording is wrong.
- If already merged, revert the merge commit in GitLab main and resync GitHub main.

Validation path:
- `openspec validate --all` - validates active OpenSpec changes and stable specs.
- `python tools/check_document_governance_rules.py --root . --json` - verifies bilingual governance/document rules.
- `python tools/check_implementation_plan_rules.py --root . --json` - verifies implementation-plan registry rules.
- `python tools/run_openspec_guard.py --root . --json` - runs the aggregate repository OpenSpec guard.
- `git diff --check` - verifies whitespace-safe diffs.

Mainline classification:
- Existing mainline maintenance under `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`.
