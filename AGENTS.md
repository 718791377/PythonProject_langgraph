# Project Instructions

- Treat this repository as the primary source of truth for Codex `subagent / omx / langgraph` user-level orchestration work.
- Do not route new implementation for this mainline back into `D:\PythonProject_OpenClaw`.
- Prefer repository startup reading before deep edits:
  - `docs_bilingual/project_startup_summary.zh-CN.md`
  - `docs_bilingual/project_startup_summary.md`
- Use `docs_bilingual/governance/openspec_official_workflow_policy.zh-CN.md` or `.md` when the question is official OpenSpec workflow authority order, bootstrap, refresh, or repository enforcement.
- Use `docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md` or `.md` when the question is where official `langgraph` should be installed, how the user-level shared LangGraph venv is laid out, how repo-local compat code is separated from the official package, how the Aliyun pip mirror should be used for LangGraph installs, or how the UTF-8-safe official LangGraph CLI wrapper should be used on Windows.
- Use `docs_bilingual/governance/user_level_launcher_payload_policy.zh-CN.md` or `.md` when the question is how user-level Codex or OMX launchers should avoid Windows command-line length failures, how large startup instructions should be passed, or where launcher payload rules belong.
- Keep native Codex as the base layer and treat oh-my-codex as an additive workflow layer around it.
- Keep `native_omx` and `langgraph` as distinct durable backend families.
- Keep the official `langgraph` package and optional `langgraph-cli[inmem]` in the user-level shared LangGraph venv by default, not in this repository tree and not in the global Python site-packages as the long-term repository rule.
- Keep repo-local LangGraph compatibility and orchestration source under `tools/langgraph_durable_orchestrator/` as the source of truth; any user-level installed helper copy is an install artifact, not the primary source.
- Keep repo-local LangGraph durable state under `.omx/state/langgraph/`; do not move repository durable state into the user-level shared venv or other shared runtime directories.
- Use `python -m pip --isolated --index-url https://mirrors.aliyun.com/pypi/simple/ ...` for LangGraph installs and upgrades; do not rely on bare `pip`, `--extra-index-url`, or persistent global pip mirror mutation as the default repository rule.
- Distinguish `installed`, `enabled`, `selected`, and `ready` states for the LangGraph lane; do not collapse those states into a single availability flag in user-facing policy or future contracts.
- Prefer `omx-langgraph-cli.ps1` over direct `langgraph.exe` help or `dev` calls on Windows terminals that are not already UTF-8 clean.
- Keep user-level launcher payloads short on Windows. Do not pass long generated orchestration instructions inline as `-c developer_instructions=...`; prefer file-backed `model_instructions_file` or another short reference path.
- Keep launcher logic thin, support-script payload assembly centralized, and installer logic generation-only; do not spread payload-length workarounds across installed wrappers.
- Use OpenSpec for durable orchestration architecture, user-level control-surface, and multi-file implementation changes.
- Run `python .\tools\run_openspec_guard.py --root .` before concluding that repository-local OpenSpec enforcement is healthy.
- Run `python .\tools\verify_official_openspec.py --root .` after bootstrap or refresh.
- Preserve the current main Codex CLI session as leader; do not redesign the system around a separate persistent leader pane.
- Keep research and implementation in different roles when the task starts open-ended.

## Publication Workflow

- Treat GitLab as the authoritative review and merge surface for this repository.
- For repository changes, create a feature branch, push it to `gitlab`, open or update a GitLab MR, wait for the GitLab pipeline to pass, and merge into GitLab `main`.
- After GitLab `main` is merged and green, sync that exact `main` commit directly to GitHub.
- Do not open GitHub PRs for this repository unless the user explicitly overrides this workflow; GitHub is the post-merge mirror/sync target by default.

## Current Mainline

- `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`

## Current Sequencing Rule

- The initial queued LangGraph-deepening mainlines from the previous roadmap are now closed.
- The earlier capability-gap sync pass is also complete.
- The bounded graph-kernel rollout is now closed as well.
- The bounded primary-runtime engine rollout is now closed as well.
- The bounded compiled-invocation rollout is now closed as well.
- The bounded live-execution rollout is now closed as well.
- The generalized live-routing rollout is now closed as well.
- The subgraph persistence and state-inspection rollout is now closed as well.
- The fuller live primary-execution-engine rollout is now closed as well.
- The richer automatic runtime-policy rollout is now closed as well.
- The broader automatic runtime-policy rollout is now closed as well.
- The deeper live primary-engine rollout is now closed as well.
- The superstep live primary-engine rollout is now closed as well.
- The stateful live primary-engine rollout is now closed as well.
- The graph-resident live primary-engine boundary-state rollout is now closed as well.
- The subgraph-aware live primary-engine handoff-state rollout is now closed as well.
- The approval-aware live primary-engine resume-state rollout is now closed as well.
- The recovery-aware live primary-engine provenance-state rollout is now closed as well.
- The durable-artifact-aware live primary-engine state rollout is now closed as well.
- The post-durable-artifact-aware capability-gap sync pass is now closed as well.
- The reducer-aware live primary-engine merge-state rollout is now closed as well.
- The post-reducer-aware capability-gap sync pass is now closed as well.
- The command-aware live primary-engine control-state rollout is now closed as well.
- The post-command-aware capability-gap sync pass is now closed as well.
- The runtime-aware live primary-engine context-store-state rollout is now closed as well.
- The post-runtime-aware capability-gap sync pass is now closed as well.
- The memory-aware live primary-engine semantic-state rollout is now closed as well.
- The post-memory-aware capability-gap sync pass is now closed as well.
- The migration-aware live primary-engine compatibility-state rollout is now closed as well.
- Treat `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` as the current follow-up sync mainline before opening any later LangGraph-deepening candidate.

## Migration Rule

- During and after migration, this repository owns the future of the Codex orchestration line.
- `D:\PythonProject_OpenClaw` may retain temporary redirect notes only and must not remain an active implementation location for this line.
