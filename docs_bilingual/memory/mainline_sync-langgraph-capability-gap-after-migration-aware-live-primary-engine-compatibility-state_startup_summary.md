---
doc_id: mainline_sync_langgraph_capability_gap_after_migration_aware_live_primary_engine_compatibility_state_startup_summary
lang: en
status: active
doc_class: startup_summary
---

# Mainline `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` Startup Summary

## Scope

This summary carries drift-prone handoff detail for the current named repository mainline:

- `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` - current named mainline for post-migration LangGraph capability-gap synchronization and adjacent operator-surface maintenance.
- `docs_bilingual/project_startup_summary.md` - stable repository-entry startup summary that points here for fast-changing execution state.
- `AGENTS.md` - repository instruction surface that remains authoritative for routing and safety reminders.

Use this file when a new session needs to know where the current mainline really stands before opening or continuing an OpenSpec change.

## Current Handoff Snapshot

Use this snapshot before older implementation notes or archived change history.

Latest landed increments:

- `archive/mr6-automatic-routing-readiness` - landed readiness-review closeout confirming that automatic durable routing hookup already exists in the earlier team-mode implementation line; do not reopen MR 6 as new runtime implementation work.
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` and `.zh-CN.md` - canonical durable-state isolation plans now state that MR 1 through MR 6 are complete and that any future live smoke or adoption gate must be a separate reviewed change.
- `fix/omx-mcp-windows-cleanup-output` - landed code change that keeps direct `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace` MCP entries enabled while suppressing benign Windows `taskkill` success output during wrapped `codex-ohmy` `/resume` cleanup.
- `archive/stabilize-omx-mcp-windows-cleanup-output` - archived OpenSpec closeout merged through GitLab MR `!74`; the archive is present under `openspec/changes/archive/2026-05-04-stabilize-omx-mcp-windows-cleanup-output/`.
- `openspec/specs/codex-user-level-windows-cleanup-output-control/spec.md` and `.zh-CN.md` - stable specs now require scoped cleanup-output control, PATH restoration, direct `omx_*` MCP preservation, and checker-backed validation.
- `openspec/specs/codex-user-level-mainline-memory-handoff/spec.md` - stable spec requiring current mainline memory handoffs to identify the latest landed increment before listing next actions.

Publication and active-change state at the start of this refresh:

- `main`, `gitlab/main`, and `github/main` - all pointed at commit `fccaf73ef45a9c9fb12a1e0f6da1bcfcf4dc11b3` after GitLab MR `!74` merged and GitHub was synchronized.
- GitLab main pipeline `#2497474485` passed for `fccaf73ef45a9c9fb12a1e0f6da1bcfcf4dc11b3`.
- `openspec list` reported no active changes before `refresh-mainline-memory-after-cleanup-output-closeout` was opened in an isolated worktree.
- Local archive worktrees for `archive/stabilize-omx-mcp-windows-cleanup-output` and `archive/mainline-memory-refresh` were removed after confirming they were clean and merged.
- `python tools/check_worktree_session_hygiene.py --root . --json` and `python tools/check_session_ownership_claims.py --root . --json` passed from `main` before this refresh branch was opened.

Current interpretation:

- MR 1 through MR 6 in the bounded durable-state rollout queue are complete.
- The automatic durable routing helper exists as generated user-level surface; future work must not duplicate the existing `omx-team-auto.ps1` behavior just to claim MR 6 is implemented.
- The Windows cleanup-output fix is implemented, installed, manually verified by `/resume`, archived, merged to GitLab `main`, and mirrored to GitHub.
- `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace` remain Codex-direct MCP entries; MCP Router remains outside those Codex-dedicated tools.
- A new session should not treat old MCP-scope, MR 5 helper mirror, MR 6 readiness, or Windows cleanup-output work as the current required implementation target.

## MCP Scope Routing Reminder

When a question involves MCP server placement, use this routing:

- `omx_state` - Codex-dedicated MCP server for oh-my-codex state surfaces; keep it as a direct Codex MCP entry, not under MCP Router shared management.
- `omx_memory` - Codex-dedicated MCP server for oh-my-codex memory surfaces; keep it as a direct Codex MCP entry, not under MCP Router shared management.
- `omx_code_intel` - Codex-dedicated MCP server for oh-my-codex code-intelligence surfaces; keep it as a direct Codex MCP entry, not under MCP Router shared management.
- `omx_trace` - Codex-dedicated MCP server for oh-my-codex trace surfaces; keep it as a direct Codex MCP entry, not under MCP Router shared management.
- `mcp_router` - Codex-side bridge entry for reaching MCP Router; keep it disabled for Codex unless the operator explicitly re-enables it for a controlled test.
- `chrome-devtools` - browser/devtools MCP capability that must remain available for projects that need browser automation.
- `pencil` - design/canvas MCP capability that must remain available for design tasks that need it.

Repository code and MRs must not mutate user-level MCP configuration or MCP Router database state unless the user explicitly asks for that operation.

## Current Change-Readiness Verdict

The repository is ready for the next small, explicitly named OpenSpec change after this handoff refresh is merged, while respecting any live local ownership claims:

- active-change state must be checked with `openspec list --json` before writing files
- local task ownership must be checked with `python tools/check_session_ownership_claims.py --root . --precheck-task ... --json` before creating a new write scope
- stale branch or remote-branch signals must be classified as completed-stale residue before a new write scope proceeds
- durable team launch is still not allowed for single-slice documentation, checker refresh, or readiness-review work
- Local `main` is the primary integration surface; GitLab and GitHub remain remote publication and mirror surfaces

## Safe Next Actions For A New Session

After this refresh lands, choose one of these next actions explicitly before writing files:

1. `durable routing smoke/adoption gate` - only if the user explicitly names the target repository, phase, task, and operator consent boundary; open a separate reviewed OpenSpec change and start with dry-run or read-only evidence before any `-Apply` action.
2. `strict MCP Router audit` - run `python tools/check_mcp_router_scope_policy.py --root . --strict-router-state --json` to inspect local MCP Router drift, then report manual cleanup guidance without editing the database.
3. `skills context budget follow-up` - open a separate user-level skills governance change if the operator wants to reduce skill-description warnings without deleting browser, Vercel, or design capabilities.
4. `new active implementation slice` - create a fresh OpenSpec change only after confirming there are no active changes or after explicitly taking ownership of an existing active change.

## Important Non-Drift Notes

- This repository owns the Codex orchestration line; do not resume new implementation for this line in `D:\PythonProject_OpenClaw`.
- `D:\PythonProject_OpenClaw`, `D:\PythonProject_CLIProxyAPI`, and `D:\project` are consumer projects that keep their own repo-local facts and durable state.
- Browser automation capability remains available for projects that need it; do not remove browser or Vercel-related skills just to reduce startup context.
- User-level skills and `C:\Users\lenovo\.codex\config.toml` are out of scope unless the user explicitly authorizes that operation.
- PowerShell console mojibake on Chinese docs is an output-encoding issue unless Python UTF-8 reads confirm source corruption.
