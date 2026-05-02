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

- `codex-direct-browser-design-mcp-policy` - landed policy change that keeps browser/design MCP capability available and prevents MCP-scope cleanup from disabling required browser or design automation surfaces.
- `archive/codex-direct-browser-design-mcp-policy` - archived OpenSpec closeout merged through GitLab; the archive is present under `openspec/changes/archive/2026-05-02-codex-direct-browser-design-mcp-policy/`.
- `sync-durable-rollout-plan-status` - landed OpenSpec change that updates the cross-session durable-state isolation plan so MR 5 helper mirror source-of-truth work is no longer described as the next active durable-state slice.
- `docs/fix-status-sync-chinese-text` - landed follow-up that replaced corrupted question-mark placeholder text in Chinese status-sync artifacts with readable UTF-8 Chinese.
- `archive/sync-durable-rollout-plan-status` - archived OpenSpec closeout merged through GitLab; the archive is present under `openspec/changes/archive/2026-05-02-sync-durable-rollout-plan-status/`.
- `openspec/specs/codex-user-level-team-mode-plan-status-sync/spec.md` and `.zh-CN.md` - stable specs now require durable-state rollout queues not to point at already archived slices as next active work.
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` and `.zh-CN.md` - canonical durable-state isolation plans now mark MR 5 as completed and reframe MR 6 or an MR 6 readiness review as the next decision point.
- `codex-user-level-mcp-scope-policy` and `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` / `.zh-CN.md` - stable MCP scope policy remains the routing authority for Codex-direct versus MCP Router-managed MCP entries.
- `openspec/specs/codex-user-level-mainline-memory-handoff/spec.md` - stable spec requiring current mainline memory handoffs to identify the latest landed increment before listing next actions.

Publication and active-change state at the start of this refresh:

- `main`, `gitlab/main`, and `github/main` - all pointed at commit `b8223434bf873d93c22ab82ac26ec095e99e0576` in the local clone checked before `refresh-mainline-memory-after-durable-rollout-status-sync` was opened.
- GitLab main pipeline `#2495016689` passed for `b8223434bf873d93c22ab82ac26ec095e99e0576`.
- `openspec list --json` reported an empty `changes` array before this refresh change was opened in an isolated worktree.
- `refresh-mainline-memory-after-durable-rollout-status-sync` is the current handoff-refresh OpenSpec change. It refreshes memory only; archive should be serialized later if another live session still owns broad `openspec/specs` scope.

Current interpretation:

- The Codex direct browser/design MCP policy is implemented, archived, merged to GitLab `main`, and mirrored to GitHub.
- The durable rollout plan status-sync work is implemented, Chinese text repaired, archived, merged to GitLab `main`, and mirrored to GitHub.
- A new session should not reopen MR 5 helper mirror source-of-truth work; it is completed and part of the implemented baseline.
- A new session should not treat old replay, diff-approval, task-ownership precheck, MCP-scope, or durable-rollout MR 5 work as the current required implementation target.

## MCP Scope Routing Reminder

When a question involves MCP server placement, use this routing:

- `omx_state` - Codex-dedicated MCP server for oh-my-codex state surfaces; keep it as a direct Codex MCP entry, not under MCP Router shared management.
- `omx_memory` - Codex-dedicated MCP server for oh-my-codex memory surfaces; keep it as a direct Codex MCP entry, not under MCP Router shared management.
- `omx_code_intel` - Codex-dedicated MCP server for oh-my-codex code-intelligence surfaces; keep it as a direct Codex MCP entry, not under MCP Router shared management.
- `omx_trace` - Codex-dedicated MCP server for oh-my-codex trace surfaces; keep it as a direct Codex MCP entry, not under MCP Router shared management.
- `mcp_router` - Codex-side bridge entry for reaching MCP Router; Codex may keep this direct entry, but MCP Router must not manage itself as a child server.
- `chrome-devtools` - browser/devtools MCP capability that must remain available for projects that need browser automation.
- `pencil` - design/canvas MCP capability that must remain available for design tasks that need it.

Repository code and MRs must not mutate user-level MCP configuration or MCP Router database state unless the user explicitly asks for that operation.

## Current Change-Readiness Verdict

The repository is ready for the next small, explicitly named OpenSpec change after this handoff refresh is merged, while respecting any live local ownership claims:

- current startup surfaces have dedicated pointers for MCP scope, worktree isolation, and durable-state status-sync boundaries
- active-change state must be checked with `openspec list --json` before writing files
- local task ownership must be checked with `python tools/check_session_ownership_claims.py --root . --precheck-task ... --json` before creating a new write scope
- durable team launch is still not allowed for single-slice documentation, checker refresh, or readiness-review work
- GitLab remains the authoritative MR and merge surface; GitHub remains the post-merge mirror

## Safe Next Actions For A New Session

After this refresh lands, choose one of these next actions explicitly before writing files:

1. `MR 6 readiness review` - create or continue a separately named OpenSpec change that reviews whether MR 3 through MR 5 evidence is still sufficient before automatic durable routing hookup.
2. `automatic durable routing hookup` - only after MR 6 readiness is accepted, connect real task-flow thresholds to `native_omx` / `langgraph` selection through a separate reviewed change.
3. `strict MCP Router audit` - run `python tools/check_mcp_router_scope_policy.py --root . --strict-router-state --json` to inspect local MCP Router drift, then report manual cleanup guidance without editing the database.
4. `archive this memory refresh` - only if no active session owns overlapping `openspec/specs` scope; perform the archive in a serialized archive worktree.
5. `new OpenSpec change` - create a fresh change only after confirming there are no active changes or after explicitly taking ownership of an existing active change.

## Important Non-Drift Notes

- This repository owns the Codex orchestration line; do not resume new implementation for this line in `D:\PythonProject_OpenClaw`.
- `D:\PythonProject_OpenClaw`, `D:\PythonProject_CLIProxyAPI`, and `D:\project` are consumer projects that keep their own repo-local facts and durable state.
- Browser automation capability remains available for projects that need it; do not remove browser or Vercel-related skills just to reduce startup context.
- User-level skills and `C:\Users\lenovo\.codex\config.toml` are out of scope unless the user explicitly authorizes that operation.
- PowerShell console mojibake on Chinese docs is an output-encoding issue unless Python UTF-8 reads confirm source corruption.
