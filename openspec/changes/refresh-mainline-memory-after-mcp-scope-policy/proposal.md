## Why

The current mainline memory handoff still points cold-start sessions at older replay and task-ownership work even though the MCP Router scope policy and the mainline memory handoff archival work have now landed. This can mislead a new session into reopening completed work instead of starting the next small OpenSpec change from the real current state.

## What Changes

- Refresh the startup-facing mainline memory summary so it identifies the latest landed MCP scope and memory-handoff increments before listing next actions.
- Add the MCP scope governance document to startup read order and repository instruction routing so MCP Router versus Codex-direct MCP questions land on the right policy.
- Keep the update documentation-only: no runtime launcher, user-level configuration, MCP Router database, or durable state is changed.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-mainline-memory-handoff` - existing OpenSpec capability that defines how current mainline memory summaries keep cold-start handoffs aligned with the latest landed governance, checker, tooling, or workflow increment.

## Impact

Impact scope:

- `docs_bilingual/project_startup_summary.md` - English startup summary that lists cold-start read order and current repository posture.
- `docs_bilingual/project_startup_summary.zh-CN.md` - Chinese companion for the startup summary.
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - English drift-prone memory handoff for the current named mainline.
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - Chinese companion for the current named mainline memory handoff.
- `AGENTS.md` - repository instruction surface that routes future MCP-scope questions to the stable policy document.
- `openspec/changes/refresh-mainline-memory-after-mcp-scope-policy/` - OpenSpec change directory for this documentation refresh.

Explicit non-goals:

- Do not modify `C:\Users\lenovo\.codex\config.toml`; that file is the user-level Codex configuration and is outside this repository change.
- Do not modify MCP Router database or UI state; MCP Router state must be changed manually by the operator when required.
- Do not enable, disable, launch, or delete any durable team, LangGraph state, or native OMX state.
- Do not change Codex-dedicated MCP server installation; this change only clarifies handoff text.

Rollout sequence:

1. Create this OpenSpec change and bilingual artifacts.
2. Refresh startup summary, AGENTS routing, and current mainline memory files.
3. Run OpenSpec and repository governance checks locally.
4. Publish through the GitLab-first MR flow, then sync the exact merged `main` commit to GitHub.

Rollback plan:

- Revert the documentation commit or restore the previous startup and memory summary files from Git history.
- No runtime or user-level state rollback is required because this change does not write outside the repository.

Validation path:

- `openspec validate --all` - validates all OpenSpec changes and stable specs.
- `python tools/run_openspec_guard.py --root . --json` - runs the repository OpenSpec guard and governance checker bundle.
- `python tools/check_document_governance_rules.py --root . --json` - checks registered governance document consistency.
- `python tools/check_name_clarity_rules.py --root . --json` - checks that code-like names in docs have short explanations.
- `git diff --check` - checks whitespace and patch formatting.

Mainline classification:

- Existing mainline: `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` - current named repository mainline for post-migration LangGraph capability-gap synchronization and adjacent operator-surface maintenance.
