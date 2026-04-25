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

- GitLab is the authoritative review and merge surface for this repository.
- Feature branches open or update GitLab MRs first; GitLab pipeline success gates the merge into GitLab `main`.
- GitHub is the post-merge sync target: after GitLab `main` is merged and green, push the same `main` commit directly to GitHub.
- Do not open GitHub PRs by default.

Stable capability posture:

- `subagent`
  - already production-usable at the leader layer
- `native_omx`
  - already production-usable as the worker-centric durable lane on native Windows
- `langgraph`
  - already a real additive durable backend
  - still usable but MVP-shaped rather than a fully realized LangGraph-native runtime

Drift-prone execution detail now lives in the mainline memory summary rather than this repository-entry summary.

## Cold-Start Read Order

1. this file
2. `docs_bilingual/project_startup_summary.zh-CN.md`
3. `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md`
4. `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md`
5. `AGENTS.md`
6. `docs_bilingual/governance/langgraph_user_level_runtime_policy.md`
7. `docs_bilingual/governance/user_level_launcher_payload_policy.md`
8. `docs_bilingual/governance/openspec_usage_convention.md`
9. `docs_bilingual/governance/openspec_opsx_project_usage_policy.md`
10. `docs_bilingual/governance/openspec_official_workflow_policy.md`
11. `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md`
12. `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md`
13. the active OpenSpec change being implemented

## Current Mainline

- `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`

## Active Detail Location

For drift-prone execution detail, read:

- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md`
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md`

That mainline memory summary carries:

- the current maintenance lane
- latest session-carried operator workflow changes
- the frozen next-change brief
- the current change-readiness verdict

For the detailed post-mainline LangGraph queue, read:

- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md`
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md`

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
