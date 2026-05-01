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

- `formalize-mcp-router-scope-policy` - archived OpenSpec change that established which MCP servers belong in Codex direct configuration and which may be managed through MCP Router.
- `codex-user-level-mcp-scope-policy` - stable OpenSpec capability that records MCP Router scope requirements and self-management exclusions.
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` - English governance policy for MCP Router shared management versus Codex-dedicated direct MCP entries.
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md` - Chinese companion for the MCP scope governance policy.
- `tools/check_mcp_router_scope_policy.py` - checker that verifies repository policy and can optionally perform strict local MCP Router state checks.
- `refresh-mainline-memory-after-task-ownership-precheck` - archived OpenSpec change that introduced the stable mainline memory handoff requirement.
- `openspec/specs/codex-user-level-mainline-memory-handoff/spec.md` - stable spec requiring current mainline memory handoffs to identify the latest landed increment before listing next actions.

Publication and active-change state at the start of this refresh:

- `main`, `gitlab/main`, and `github/main` - repository publication refs that pointed at commit `f6cc0f6` in the local clone checked before this refresh branch was created.
- `openspec list --json` - active-change inventory command; it reported an empty `changes` array before `refresh-mainline-memory-after-mcp-scope-policy` was opened.
- `refresh-mainline-memory-after-mcp-scope-policy` - the current OpenSpec change for refreshing this handoff; after it is merged and archived, a future session should again expect no active changes unless a newer change exists.

Current interpretation:

- The MCP Router scope policy is implemented, archived, and mirrored to GitHub.
- The mainline memory handoff requirement is implemented and archived.
- A new session should not reopen the MCP Router scope design unless new evidence appears.
- A new session should not treat old replay, diff-approval, or task-ownership precheck work as the current required implementation target.

## MCP Scope Routing Reminder

When a question involves MCP server placement, use this routing:

- `omx_state` - Codex-dedicated MCP server for oh-my-codex state surfaces; keep it as a direct Codex MCP entry, not under MCP Router shared management.
- `omx_memory` - Codex-dedicated MCP server for oh-my-codex memory surfaces; keep it as a direct Codex MCP entry, not under MCP Router shared management.
- `omx_code_intel` - Codex-dedicated MCP server for oh-my-codex code-intelligence surfaces; keep it as a direct Codex MCP entry, not under MCP Router shared management.
- `omx_trace` - Codex-dedicated MCP server for oh-my-codex trace surfaces; keep it as a direct Codex MCP entry, not under MCP Router shared management.
- `mcp_router` - Codex-side bridge entry for reaching MCP Router; Codex may keep this direct entry, but MCP Router must not manage itself as a child server.
- `chrome-devtools` - shared browser/devtools MCP server candidate that may be managed by MCP Router when other IDEs also need it.
- `pencil` - shared MCP server candidate that may be managed by MCP Router when multiple clients need it.

Repository code and MRs must not mutate user-level MCP configuration or MCP Router database state unless the user explicitly asks for that operation.

## Current Change-Readiness Verdict

The repository is ready for the next small, explicitly named OpenSpec change after this handoff refresh is merged or archived:

- current startup surfaces have a dedicated MCP scope policy pointer
- active-change state must be checked with `openspec list --json` before writing files
- durable team launch is still not allowed for single-slice documentation or checker refresh work
- GitLab remains the authoritative MR and merge surface; GitHub remains the post-merge mirror

## Safe Next Actions For A New Session

After this refresh lands, choose one of these next actions explicitly before writing files:

1. `strict MCP Router audit` - run `python tools/check_mcp_router_scope_policy.py --root . --strict-router-state --json` to inspect local MCP Router drift, then report manual cleanup guidance without editing the database.
2. `durable-state status hardening` - continue the active durable-state isolation plan by improving read-only status reporting, without launching a durable team.
3. `general template follow-up` - continue the local Git plus OpenSpec plus native subagent template work only in its own project or a dedicated branch.
4. `new OpenSpec change` - create a fresh change only after confirming there are no active changes or after explicitly taking ownership of the existing active change.

## Important Non-Drift Notes

- This repository owns the Codex orchestration line; do not resume new implementation for this line in `D:\PythonProject_OpenClaw`.
- `D:\PythonProject_OpenClaw`, `D:\PythonProject_CLIProxyAPI`, and `D:\project` are consumer projects that keep their own repo-local facts and durable state.
- Browser automation capability remains available for projects that need it; do not remove browser or Vercel-related skills just to reduce startup context.
- PowerShell console mojibake on Chinese docs is an output-encoding issue unless Python UTF-8 reads confirm source corruption.
