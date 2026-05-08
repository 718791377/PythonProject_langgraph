# Project Instructions

- Treat this repository as the primary source of truth for Codex `subagent / omx / langgraph` user-level orchestration work.
- Do not route new implementation for this mainline back into `D:\PythonProject_OpenClaw`.
- Prefer repository startup reading before deep edits:
  - `docs_bilingual/project_startup_summary.zh-CN.md`
  - `docs_bilingual/project_startup_summary.md`
- Use `docs_bilingual/governance/openspec_official_workflow_policy.zh-CN.md` or `.md` when the question is official OpenSpec workflow authority order, bootstrap, refresh, or repository enforcement.
- Use `docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md` or `.md` when the question is where official `langgraph` should be installed, how the user-level shared LangGraph venv is laid out, how repo-local compat code is separated from the official package, how the Aliyun pip mirror should be used for LangGraph installs, or how the UTF-8-safe official LangGraph CLI wrapper should be used on Windows.
- Use `docs_bilingual/governance/user_level_launcher_payload_policy.zh-CN.md` or `.md` when the question is how user-level Codex or OMX launchers should avoid Windows command-line length failures, how large startup instructions should be passed, or where launcher payload rules belong.
- Use `docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md` or `.md` when the question is whether an MCP server belongs in Codex direct config, MCP Router shared management, or neither; this policy also covers `mcp_router` self-management and Codex-dedicated `omx_*` MCP entries.
- Use `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md` or `.md` when the question involves multiple Codex sessions, dirty files, Git worktrees, feature branches, local `main`, `gitlab/main`, or GitHub sync safety.
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
- Do not rely on prompt reminders alone for system-level, user-level, or project-level safety boundaries; pair them with script controls such as checkers, guarded helpers, CI gates, or generated launcher logic.
- Do not duplicate the context-retention canary prompt in `AGENTS.md`; its literal prompt text lives only in `docs_bilingual/project_startup_summary.md` and `docs_bilingual/project_startup_summary.zh-CN.md`. If startup-summary context-loss detection triggers, reread `docs_bilingual/project_startup_summary.md` and follow its cold-start read order before continuing.

- Treat resumed legacy Codex sessions as compatibility-scoped sessions. A resumed legacy Codex session is an older `/resume` thread that may still carry stale runtime or MCP startup assumptions; it may continue for follow-up discussion but must not override current repository governance.
- For legacy-session MCP failures, prefer per-invocation overrides such as `-c "mcp_servers.omx_code_intel.enabled=false"`. This `-c` argument is a one-launch Codex config override for a single old thread, not a permanent edit to `C:\Users\lenovo\.codex\config.toml`, which is the user-level Codex configuration file.

## Publication Workflow

- Treat GitLab as the authoritative review and merge surface for this repository.
- Use local-first batching to conserve GitLab runner minutes. GitLab runner minutes are the remote CI quota consumed by GitLab pipelines, so related local commits should be validated together before the first push.
- Use a local-first plus mirrored CI/MR gate. Local CI is the primary check logic, local MR review is the pre-remote review surface, and GitLab CI/MR remains the clean-environment confirmation and audit-record layer.
- Keep the primary directory and local mainline fresh without turning `main` into a feature workspace. `D:\PythonProject_langgraph` is the primary main worktree: it must be checked out on local `main`; its HEAD must not lag behind local `main`; and in normal operation its HEAD should exactly equal the local `main` branch reference.
- Keep local `main` from falling behind the authoritative remote. Before new writable work, release-timing judgment, push, MR creation/update, or mainline-state claims, fetch `gitlab/main` and ensure local `main` is not behind the latest `gitlab/main`; if local `main` is behind, fast-forward it before continuing. If the primary directory is dirty or not on `main`, stop writable work and resolve the hygiene issue first. Writable feature work must still happen in a dedicated feature worktree / feature branch, not directly in the primary `main` worktree.
- For repository changes, create a feature branch and do local commits, local checker runs, and local cleanup before pushing to `gitlab`. The `gitlab` remote is the authoritative GitLab repository remote used only when the local branch is ready for MR validation.
- Before pushing a feature branch for remote MR review, run the shared local CI gate `tools/ci/local_gate.ps1` and the local MR review gate `tools/ci/local_mr_review.ps1` after all intended changes are committed and the feature worktree is clean, unless the user explicitly requests an early remote pipeline check.
- Local CI and remote CI must reuse `tools/ci/local_gate.ps1`. Remote CI configuration may install required tools and invoke the shared script, but must not maintain a divergent checker sequence. `tools/check_local_mirrored_ci_gate.py` verifies this wiring through the repository guard.
- If local gate results and remote CI results differ, fix the shared scripts, environment setup, or configuration drift; do not bypass either local or remote gate.
- For a locally completed OpenSpec change that is ready for publication, default to a single-MR archive package: after local implementation validation, archive the change on the same feature branch, promote its delta spec into stable spec, re-run local validation, and then open one GitLab MR containing implementation, archive movement, and stable spec updates.
- Use the single-MR archive package for small governance, documentation, checker, and test changes when local validation already proves completion. Use a two-MR flow only when the change is large or risky, needs remote CI or MR review before archive, would create heavy stable-spec conflicts, or the user explicitly requests an implementation-only MR.
- Batch related small changes into one GitLab MR when they share the same topic and rollback boundary; do not combine unrelated topics just to save runner minutes.
- Before remote publication, the active session's model must judge whether the local batch is ready to publish and present a recommendation to the user, including whether the batch uses the single-MR archive package or a justified two-MR exception. The user remains the release decision authority.
- Push to GitLab and open or update a GitLab MR only after local CI and local MR review pass, unless the user explicitly requests an early remote pipeline check.
- Wait for the GitLab pipeline to pass, then merge into GitLab `main`.
- After GitLab `main` is merged and green, sync that exact `main` commit directly to GitHub.
- Do not open GitHub PRs for this repository unless the user explicitly overrides this workflow; GitHub is the post-merge mirror/sync target by default.

## Current Mainline

- `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`

## Current Implementation Boundary

- Active implementation now follows these two implementation plans:
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md`: the active user-level team-mode plan for native Codex, oh-my-codex, native_omx, and LangGraph routing behavior.
  - `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md`: the active durable-state isolation plan that keeps repo-local state from leaking across projects or sessions.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` is the long-term final-target draft for a personal production-grade persistent Codex CLI team; do not treat it as implemented runtime behavior.
- `D:\PythonProject_OpenClaw`, `D:\PythonProject_CLIProxyAPI`, `D:\project`, and future projects are consumer projects for shared user-level runtime and policy only. Each project keeps its own OpenSpec artifacts, durable state, CI status, publication state, and repo-local facts.
- Preserve browser automation capability for projects that need it, especially `D:\PythonProject_OpenClaw` and `D:\PythonProject_CLIProxyAPI`; do not disable Vercel or browser-related skills globally as a shortcut for reducing skill context.
- Do not auto-launch a durable team during startup, boundary-freeze work, or read-only state inventory. Durable team launch requires a frozen plan plus at least two mostly independent execution slices.

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
