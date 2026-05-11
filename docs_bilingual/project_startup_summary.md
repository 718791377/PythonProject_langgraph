---
doc_id: project_startup_summary
lang: en
status: active
doc_class: startup_summary
---

# Project Startup Summary

## Goal

This repository is the primary home for the Codex user-level orchestration line:

- native Codex subagents
- oh-my-codex user-level workflow surfaces
- OMX durable-team orchestration
- LangGraph durable orchestration

Use a three-layer model for LangGraph in this repository: the user-level shared layer provides the official shared runtime and tooling across projects, this repository is the project-level handoff layer that owns the repo-local compatibility or orchestration source and startup-facing policy, and repo-local durable truth stays under `.omx/state/langgraph/`. Any generated user-level helper copy is an install artifact only, not the source of truth.

## Current Repository Posture

Stable repository-entry posture:

- foundation complete
- this repository remains the primary repository for the user-level Codex orchestration line
- the current named repository mainline is `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`

Stable publication posture:

- Publication is local-main-first: local `main` is the primary integration surface after local validation, local MR review, a clean feature worktree, and explicit user approval.
- GitLab is no longer the default authority gate before local `main` integration. GitLab remains the remote publication, clean-environment confirmation, backup, and audit surface; GitHub remains the mirror/sync target unless the user explicitly overrides that workflow.
- Use local-first batching to conserve GitLab runner minutes. GitLab runner minutes are the remote CI quota consumed by GitLab pipelines, so do local commits, local checks, local MR review, and local cleanup before the first remote push.
- Local CI and remote CI must reuse `tools/ci/local_gate.ps1`; remote CI configuration should install required tools and invoke that shared script rather than duplicating checker commands. CI-managed tests are listed in `tools/ci/ci_test_manifest.json` to keep the gate stable. Local MR review uses `tools/ci/local_mr_review.ps1` after all intended changes are committed and the feature worktree is clean, before local `main` integration or remote publication.
- Keep local `main` current with `gitlab/main` before new writable work, release-timing judgment, remote push, MR creation, or local alignment claims. Local-first batching is not permission to work from a stale remote base.
- Local `main` may intentionally lead `gitlab/main` and `github/main` after approved local integration. Report that remote lag clearly until GitLab/GitHub publication or mirror sync catches up.
- Feature branches open or update GitLab MRs only after local CI and local MR review pass, unless the user explicitly requests an early remote pipeline check.
- If local and remote CI results differ, fix the shared scripts, environment setup, or configuration drift instead of bypassing either evidence layer.
- Batch related small changes into one integration package when they share the same topic and rollback boundary; do not combine unrelated topics just to save runner minutes.
- Before local integration or remote publication, the active session's model judges whether the local batch is ready and recommends publish/integrate or wait to the user. The user remains the release decision authority.
- GitHub PRs are not opened by default.

Stable capability posture:

- `subagent` - native Codex leader-side specialist agent capability.
  - already production-usable at the leader layer
- `native_omx` - oh-my-codex worker-centric durable execution lane.
  - already production-usable as the worker-centric durable lane on native Windows
- `langgraph` - LangGraph-backed additive durable orchestration backend.
  - already a real additive durable backend
  - still usable but MVP-shaped rather than a fully realized LangGraph-native runtime


Stable legacy-session compatibility posture:

- A legacy resumed session is an older Codex `/resume` thread that may still carry stale runtime, MCP, or launcher assumptions from before the latest governance updates.
- Legacy resumed sessions may continue temporarily for follow-up discussion, but new governance implementation, dirty-file ownership, and release decisions must use the current repository documents and current local Git state.
- Start `codex-ohmy` first when possible, then enter `/resume` from that temporary session. `codex-ohmy` is the stable wrapped Codex entrypoint for normal user-level orchestration work.
- If one old thread has an MCP startup problem, use a per-invocation override such as `-c "mcp_servers.omx_code_intel.enabled=false"` only for that old thread. The override is a one-launch config value and must not become a permanent user-level config edit.
- Do not globally disable `omx_state`, `omx_memory`, `omx_code_intel`, `omx_trace`, `chrome-devtools`, or `pencil` just because a legacy resumed session fails. These names are direct Codex MCP servers that provide orchestration state, memory, code intelligence, trace inspection, browser debugging, and design access.

## Current Implementation Boundary

The current implementation lane is limited to the active user-level orchestration plans:

- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - active plan that governs user-level team mode and routing behavior.
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` - active plan that governs repo-local durable-state isolation.

The long-term north-star plan remains draft-only:

- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` - the draft final target for a personal production-grade persistent Codex CLI team; do not treat this as implemented behavior yet.

Cross-project usage rule:

- `D:\PythonProject_OpenClaw` - a consumer project that may reuse user-level Codex orchestration policy and browser automation capability, while keeping its repo-local facts and `.omx/state/` separate.
- `D:\PythonProject_CLIProxyAPI` - a consumer project that may need browser or endpoint verification, while keeping its repo-local facts and `.omx/state/` separate.
- `D:\project` - a general project root that should start with the core profile and add browser, web, or orchestration capability only when project evidence requires it.
- Future projects - consumers of shared user-level runtime and policy only; each project owns its own OpenSpec artifacts, durable state, CI status, and publication state.

Do not auto-launch a durable team during startup or boundary-freeze work. Durable-team launch is allowed only after a plan is frozen and at least two mostly independent execution slices exist.

Current no-touch durable-state baseline:

- `docs_bilingual/memory/cross_project_durable_state_read_only_inventory_2026-04-25.md` - read-only Phase 0 inventory for `D:\PythonProject_langgraph`, `D:\PythonProject_OpenClaw`, `D:\PythonProject_CLIProxyAPI`, and `D:\project`; use it as implementation evidence, not as permission to mutate `.omx/state`.

Drift-prone execution detail now lives in the mainline memory summary rather than this repository-entry summary.

## Cold-Start Read Order

1. this file
2. `docs_bilingual/project_startup_summary.zh-CN.md` - Chinese companion for this startup summary.
3. `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - English memory summary for the current mainline.
4. `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - Chinese memory summary for the current mainline.
5. `AGENTS.md` - repository and user-level Codex instruction surface.
6. `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md` - governance policy for multi-session Git worktree isolation, dirty-file handling, and mainline sync safety.
7. `docs_bilingual/governance/langgraph_user_level_runtime_policy.md` - governance policy for user-level LangGraph runtime layout and usage.
8. `docs_bilingual/governance/user_level_launcher_payload_policy.md` - governance policy for Windows-safe launcher payload handling.
9. `docs_bilingual/governance/openspec_usage_convention.md` - governance policy for how this repository uses OpenSpec.
10. `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` - governance policy for Codex-direct MCP entries versus MCP Router shared management boundaries.
11. `docs_bilingual/governance/openspec_opsx_project_usage_policy.md` - governance policy for repository OPSX workflow usage.
12. `docs_bilingual/governance/openspec_official_workflow_policy.md` - governance policy for official OpenSpec workflow authority and enforcement.
13. `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - active implementation plan for user-level team mode and orchestration routing.
14. `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` - active implementation plan for cross-session durable-state isolation.
15. the active OpenSpec change being implemented, if one exists; if `openspec list --json` reports no changes, stop here and choose the next small change explicitly before writing files.

## Context Retention Canary And Safety Enforcement

User-level safety rule:

- System-level, user-level, and project-level safety boundaries must use script control plus prompt reminders. Prompt text alone is not sufficient for boundaries that affect durable state, publication, cleanup, activation, or cross-project scope.
- Script control means executable checkers, guarded helpers, CI gates, or generated launcher logic that fail closed for a cold-start model with no previous conversation context.
- Prompt reminder means startup and plan text that explains what the script protects and what the model should reread when it appears to have forgotten the rule.

Context-retention canary:

- The literal canary prompt is maintained only in this startup summary pair: `docs_bilingual/project_startup_summary.md` and `docs_bilingual/project_startup_summary.zh-CN.md`. Other active instruction surfaces may point here, but must not duplicate the literal start/end phrase.
- Complete assistant responses for this repository's orchestration work should start with `指挥官` and end with `喵~`, unless a higher-priority system or developer instruction prevents it.
- If a complete response misses that canary after this startup summary should have been read, treat it as possible context loss.
- Recovery action: reread `AGENTS.md`, reread this startup summary pair, follow the cold-start read order above, then reread only the task-specific files needed to continue safely.

## Current Mainline

- `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` - current mainline identifier for the LangGraph capability-gap synchronization pass.

## Active Detail Location

For drift-prone execution detail, read:

- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - English memory summary carrying drift-prone details for the current mainline.
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - Chinese memory summary carrying drift-prone details for the current mainline.

That mainline memory summary carries:

- the current maintenance lane
- latest session-carried operator workflow changes
- the frozen next-change brief
- the current change-readiness verdict

For the detailed post-mainline LangGraph queue, read:

- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - the bilingual documentation path for repository governance or planning guidance
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` - the bilingual documentation path for repository governance or planning guidance

That detailed queue belongs in the implementation plan layer, not in this startup summary.

## Scope Boundary

This repository owns the user-level Codex orchestration product line.

For LangGraph specifically, this repository owns the repo-local compatibility source and repo-local durable-state contract. The shared user-level LangGraph venv is the install location for the official upstream package, not this repository tree.

For user-level launcher behavior specifically, this repository also owns the startup payload policy that prevents Windows command-line length failures in wrapped Codex entrypoints.

It does not own:

- OpenClaw application runtime work
- OpenClaw service orchestration
- OpenClaw repository-local WeCom and local-control mainlines

## Non-Drift Rule

- continue the orchestration line here only
- do not resume new implementation for this line in `D:\PythonProject_OpenClaw`
- migrate OpenSpec history with the code
- keep startup summaries and current mainline status updated before large implementation waves
