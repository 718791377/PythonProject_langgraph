---
doc_id: general_template_phase0_update_patch_plan
lang: en
canonical: docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md
translation: docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.zh-CN.md
status: active
doc_class: implementation_plan
created_at: 2026-04-25
updated_at: 2026-05-25
phase: 0
target_template: D:\PythonProject_General
source_context:
  - docs_bilingual/project_startup_summary.md
  - docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md
  - docs_bilingual/implementation_plans/codex_langgraph_repository_split_migration_plan.md
  - docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md
  - docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md
  - docs_bilingual/implementation_plans/codex_user_level_skills_governance_and_profiles_plan.md
  - D:\PythonProject_General\docs_bilingual\implementation_plans\pythonproject_general_codex_multi_project_template_upgrade_plan.md
  - D:\PythonProject_General\docs_bilingual\implementation_plans\pythonproject_general_codex_multi_project_template_upgrade_plan.zh-CN.md
---

# D:\PythonProject_General Phase 0 Template Update Patch Plan

> Cold-start contract: this plan is self-contained. A new Codex session with no prior chat context can read this file, `README.md`, `AGENTS.md`, `project_startup_summary.md`, and `docs_bilingual/governance/template_completion_protocol.md`, then implement the Phase 0 patch safely in `D:\PythonProject_General`.

## Bilingual Alignment Status

- English ASCII file: this file is the implementation source of truth.
- Chinese companion: `docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.zh-CN.md`.
- Alignment rule: keep both files synchronized for source context, scope, safety rules, deliverables, validation commands, and acceptance criteria.
- Current finding: Phase 0 is a small safety and testability patch for the master template root. It is not the complete profile, skills-governance, browser, web, publishing, OMX, or LangGraph rollout.
- Name clarity rule: every listed script, path, command, variable, or profile name must include a short explanation so a cold-start reader can tell what it is for.


## 2026-05-25 Status Refresh

This file now records the current state after the initial Phase 0 work and the later Comet governance sync for `D:\PythonProject_General`.

Current target-template facts:

- `D:\PythonProject_General` is now a local Git repository on branch `main`; the older Phase 0 note that the master template root had no Git baseline is historical context, not the current state.
- The target template has a hydration smoke-test path, a shared local CI gate, and a local MR review helper surface. The local and remote CI/MR design still reuses target-template scripts rather than maintaining divergent check sequences.
- The later Comet sync added project-level Comet workflow skills, `docs/superpowers/` placeholders, a bilingual Comet workflow policy, a stable OpenSpec spec for Comet-controlled OpenSpec + Superpowers governance, an archived local OpenSpec change, and `tools/check_openspec_comet_superpowers_policy.py`.
- Comet is recorded as OpenSpec + Superpowers governance only. It is not native subagent evidence, not oh-my-codex, not OMX, not `native_omx`, not LangGraph, and not a durable-team backend.
- The current target-template working tree still contains the Comet governance patch as local uncommitted changes pending operator review. The pre-existing untracked `.idea/` directory remains outside the planned patch scope.
- `D:\PythonProject_General_2` is governed by a separate local-Git/OpenSpec/native-subagents-only plan and must not be treated as covered by this `General` Phase 0 plan.

Latest validation evidence recorded for the `General` target after the Comet sync:

- `git -C D:\PythonProject_General diff --check` passed after line-ending normalization.
- `openspec validate --all` passed in `D:\PythonProject_General`.
- `comet status D:\PythonProject_General --json` reported no active Comet changes.
- `comet doctor D:\PythonProject_General --json` passed for project-level Codex Comet skills and script executability; global Codex Comet skills may warn as missing because the template intentionally carries project-level skills.
- `python .\tools\test_template_hydration.py --root . --json` passed in `D:\PythonProject_General`.
- `.\tools\ci\local_gate.ps1 -Root . -Json` passed in `D:\PythonProject_General`.
- `.\tools\ci\local_mr_review.ps1 -Root . -Json -AllowDirty` passed as a draft review because the target patch was intentionally left uncommitted.

## 1. Goal

Create a small, reviewable Phase 0 patch for `D:\PythonProject_General` so the template becomes safer to maintain before larger profile, skills, browser, web, publishing, or orchestration features are added.

The patch should make the template easier to verify in three states:

1. the master template root `D:\PythonProject_General`
2. a freshly generated project created by `new-openspec-project.ps1`, the PowerShell template hydrator
3. a no-context Codex session that only knows the generated repository files

The patch must keep the General template reusable across many projects. It must not copy repository-local facts from `D:\PythonProject_langgraph`, the legacy browser consumer repository, `D:\PythonProject_CLIProxyAPI`, or any other consumer repository into the generic template as universal truth.

## 2. Source Context And Current Status

This Phase 0 plan is derived from the broader General template upgrade plan pair:

- `D:\PythonProject_General\docs_bilingual\implementation_plans\pythonproject_general_codex_multi_project_template_upgrade_plan.md` - English source upgrade plan for the target template.
- `D:\PythonProject_General\docs_bilingual\implementation_plans\pythonproject_general_codex_multi_project_template_upgrade_plan.zh-CN.md` - Chinese companion upgrade plan for the target template.

It also incorporates the local orchestration boundary from `D:\PythonProject_langgraph`:

- `project_startup_summary.md` says this repository is the source of truth for the user-level Codex orchestration line.
- `codex_cli_personal_production_durable_team_plan.md` is a long-term north-star draft, not implemented runtime behavior.
- `codex_langgraph_repository_split_migration_plan.md` keeps new orchestration implementation in `D:\PythonProject_langgraph`, not in the legacy source repository.
- `codex_oh_my_codex_user_level_team_mode_plan.md` keeps native Codex as the base layer, oh-my-codex as an additive workflow layer, `native_omx` and `langgraph` as separate durable backend families, and durable-team launch threshold-gated.
- `codex_user_level_cross_session_durable_state_isolation_plan.md` requires repo-local `.omx/state` isolation and prevents stale state from one project or session from becoming another project's activation truth.
- `codex_user_level_skills_governance_and_profiles_plan.md` requires profile-based skills governance without globally disabling browser, Vercel, GitHub, OpenSpec, or orchestration capabilities that other projects may need.

Current status:

- This file defines the Phase 0 patch to apply to `D:\PythonProject_General`.
- This repository copy of the plan records the intended and observed target-template state; target-template edits still happen only when a later step explicitly edits `D:\PythonProject_General`.
- Later Phase 1 and Phase 2 work remains out of scope until the operator explicitly expands the task; the Comet governance sync is a bounded OpenSpec + Superpowers governance update, not a broad durable-orchestration rollout.

## 3. Current Observed State

As of 2026-04-25, the target template root contains useful baseline pieces:

- OpenSpec bilingual repository starter files.
- `AGENTS.md` - the repository-level operating contract for generated Codex sessions.
- `project_startup_summary.md` and `project_startup_summary.zh-CN.md` - startup summaries for cold-start sessions.
- OpenSpec governance docs and `strict-governance` schema files - policy documents and schema gates for the structured-change workflow.
- GitHub Actions and GitLab CI guard surfaces.
- git hook templates.
- `new-openspec-project.ps1` - the PowerShell generator that copies and hydrates this template into a new project.
- Windows Explorer and PyCharm launcher helpers - optional UI entry points that call the same project generator.
- root background-process launchers: `project-background.cmd`, `project-background.ps1`, and `project-background.json` - wrappers and configuration for starting, checking, and stopping a project-local long-running process.
- `tools/project_background.py` - the Python supervisor used by the background-process launchers.
- `tools/background_keepalive.py` - the harmless default process used to prove background persistence before a real server or daemon exists.
- placeholder and OpenSpec verification scripts.

Important findings:

- Historical note: on 2026-04-25 the master template root was not yet under Git control; by 2026-05-25 it is a local Git repository on branch `main`.
- The master template root intentionally contains raw placeholders for generated repositories.
- A generated test project should have no unresolved placeholders after hydration.
- Background-process support exists and should be smoke-tested in generated projects.
- The template root `.gitignore` is too narrow for Python, Node, OpenSpec, Codex, OMX, and local runtime work.
- Some helper scripts in `D:\PythonProject_langgraph` already support `--json`; the General template helper surface should inventory this gap in Phase 0 and align JSON output in a later phase.

## 4. Phase 0 Scope

Phase 0 is limited to template maintainability and verification readiness.

In scope:

1. Add or update documentation for the Phase 0 patch plan.
2. Register this implementation plan pair in `docs_bilingual/docs_registry.yaml` if the target template uses that registry for implementation plans.
3. Update the template-root `.gitignore` for local-only runtime and tooling artifacts.
4. Add a template hydration smoke-test script that creates a temporary generated project and verifies the generated project, not the master template root, is free of unresolved placeholders.
5. Document the difference between master-template placeholders and generated-project placeholders.
6. Verify generated-project background entry points without leaving a long-running process behind.
7. Record guard surface compatibility notes, especially JSON-output differences, without forcing a broad helper rewrite.
8. Keep all changes small enough for focused review and rollback.

Out of scope for Phase 0:

- implementing profile-aware project generation
- implementing skills inventory or skills governance checks
- deleting, disabling, moving, or shortening user-level skills
- changing `C:\Users\lenovo\.codex\config.toml`, which is the user-level Codex configuration file outside the template repository
- changing global Codex, Git, npm, Python, PowerShell, Vercel, GitHub, browser, or OpenSpec plugin installations
- changing real project repositories such as `D:\PythonProject_OpenClaw`, `D:\PythonProject_CLIProxyAPI`, `D:\project`, or `D:\PythonProject_langgraph` as part of the target-template patch
- requiring a GitLab or GitHub remote for the template root
- redesigning `strict-governance`, which is the repository-local OpenSpec schema used for review and approval gates
- forcing all guard helpers to support JSON output, except for inventory notes and `tools/test_template_hydration.py --json`
- rolling out browser, web, Vercel, GitHub, publishing-profile, OMX, or LangGraph durable-state profile behavior
- treating another project's `.omx/state` as a recovery path or startup authority

## 5. Safety Rules

1. Do not edit generated child projects except inside temporary test directories created for smoke tests.
2. Do not delete user-level Codex skills or plugin cache entries.
3. Do not modify global Codex, Git, npm, Python, PowerShell, Vercel, GitHub, browser, or OpenSpec plugin configuration.
4. Do not assume the master template root should pass placeholder checks; only generated projects should pass placeholder checks.
5. Do not start long-running background processes without stopping them or confining them to `.project-runtime/`, the local runtime-state directory.
6. Do not introduce project-specific facts from `D:\PythonProject_langgraph` into the general template.
7. Do not route new implementation for the user-level orchestration line back into the legacy source repository.
8. Keep English implementation-plan files ASCII-only.
9. Keep Chinese companion files registered and updated with the English source.
10. If the current host cannot support a configured background launcher, report an honest diagnostic; do not fake success.
11. Keep repo-local durable state ignored and isolated; do not copy or reuse `.omx/state` across projects.

## 6. Deliverables

### 6.1 Documentation

Create and maintain:

- `docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md` - the English ASCII Phase 0 implementation source of truth.
- `docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.zh-CN.md` - the Chinese companion that explains the same implementation scope and safety rules.

Update if applicable in the target template:

- `docs_bilingual/docs_registry.yaml` - the bilingual document registry used by cold-start sessions and document checks.
- `README.md` - the English template overview and operator-facing usage entry.
- `README.zh-CN.md` - the Chinese template overview and operator-facing usage entry.
- `docs_bilingual/governance/template_completion_protocol.md` - the English policy for replacing template defaults with real project facts.
- `docs_bilingual/governance/template_completion_protocol.zh-CN.md` - the Chinese companion for the template completion policy.

### 6.2 Template Git Baseline

If the target template still has no Git baseline when Phase 0 is implemented, use the sequence below. As of 2026-05-25, `D:\PythonProject_General` is already a local Git repository on branch `main`, so this sequence is historical fallback guidance rather than the current expected action:

1. Run `git init` in `D:\PythonProject_General`; this creates repository metadata for the template root.
2. Create or rename the initial branch to `main`; this gives the reusable template a stable baseline branch.
3. Stage only the verified template baseline; runtime and temporary files must remain ignored.
4. Commit with a message such as `Initialize Codex production template baseline`.

Acceptance for this deliverable:

- `git -C D:\PythonProject_General status --short --branch` shows branch `main` after the commit.
- Runtime and temporary files are not staged.

### 6.3 Template Ignore Rules

Update `.gitignore` to ignore at least:

```gitignore
# Codex / OMX durable runtime state
.omx/

# Temporary and runtime state
.tmp/
.project-runtime/
openspec-guard-report.json

# Python
__pycache__/
*.pyc
.pytest_cache/
.venv/

# Node / frontend
node_modules/

# Build / coverage outputs
dist/
build/
coverage/
htmlcov/
```

Ignore entry meaning:

- `.omx/` - repository-local durable orchestration state that should not be committed.
- `.tmp/` - scratch space for template hydration tests and other temporary outputs.
- `.project-runtime/` - local background-process pid, log, heartbeat, and stop-signal state.
- `openspec-guard-report.json` - local or CI guard report output.
- Python entries - bytecode caches, pytest cache, and local virtual environments.
- Node and build entries - dependency installs, build outputs, and coverage outputs.

### 6.4 Template Hydration Smoke Test

Add:

- `tools/test_template_hydration.py` - the smoke-test runner that generates a temporary project and verifies the generated output.

Minimum behavior:

1. Locate the master template root.
2. Create a temporary output directory under `.tmp/`; `.tmp/` is the template-local scratch area ignored by Git.
3. Run `new-openspec-project.ps1 -ProjectName TemplateSmokeTest -DestinationRoot <temp> -SkipOfficialOpenSpecBootstrap`; this creates a generated project without refreshing official OpenSpec managed files.
4. Run `python tools/check_placeholders.py .` inside the generated project; this verifies that hydration replaced raw template placeholders.
5. Assert generated `tools/project_background.py` exists and is non-empty; this file is the generated project's background supervisor.
6. Run `project-background.cmd doctor` or an equivalent safe check; this validates background-entry availability without leaving a long-running process behind.
7. Treat configured launcher unavailability as an honest diagnostic on constrained hosts, but fail on tracebacks, missing files, or fake success.
8. Run guard help checks:
   - `python tools/run_openspec_guard.py --help` - confirms the generated project exposes the unified local OpenSpec guard help.
   - `python tools/verify_official_openspec.py --help` - confirms the generated project exposes the official OpenSpec verification wrapper help.
   - `python tools/enforce_openspec_policy.py --help` - confirms the generated project exposes the repository policy enforcement helper help.
   - `python tools/check_hosting_enforcement.py --help` - confirms the generated project exposes the hosting enforcement helper help.
9. Unless `--keep-temp` is passed, remove the temporary output; `--keep-temp` preserves the generated project for debugging failed smoke tests.
10. Return a non-zero exit code on failure.
11. Support `--json`; this lets CI jobs and Codex sessions read a machine-parseable report.

Recommended command:

```powershell
python tools/test_template_hydration.py --root . --json
```

This command runs the template hydration smoke test against the current template root and emits a JSON report.

### 6.5 Guard Surface Compatibility Notes

Phase 0 should record, but not necessarily fix, differences between `D:\PythonProject_langgraph` and `D:\PythonProject_General` guard helper capabilities.

Known differences to inspect later:

- Some `D:\PythonProject_langgraph` helper scripts support `--json`.
- Some `D:\PythonProject_General` helper scripts may not yet support `--json`.

The safe sequence is:

1. record the inventory in Phase 0
2. add uniform JSON output in a later phase
3. avoid broad helper rewrites inside this small safety patch

## 7. Implementation Steps After Confirmation

1. Create a timestamped backup archive of `D:\PythonProject_General` unless Git has already captured a clean baseline.
2. Add or update the Phase 0 implementation plan pair in the target template if needed.
3. Register the plan pair in `docs_bilingual/docs_registry.yaml` if the target template uses that registry for implementation plans.
4. Update `.gitignore` with local runtime and tool artifacts so generated logs, caches, and scratch directories do not become commits.
5. Add `tools/test_template_hydration.py`, the smoke-test runner for generated-project hydration.
6. Run the template hydration smoke test.
7. Run targeted checks against the plan files:
   - English file has zero non-ASCII characters.
   - Both files have no trailing whitespace.
   - Both files are registered in `docs_bilingual/docs_registry.yaml` if that registry is used for implementation plans.
8. Verify generated-project placeholder scanning through the smoke test.
9. If the template root is not a Git repository, initialize Git, set branch `main`, and commit the verified baseline.
10. Defer profile, skills, publishing, browser, web, OMX, and LangGraph broad rollout until Phase 0 passes unless the user explicitly asks to bundle later phases.

## 8. Validation Commands

Run from `D:\PythonProject_General` unless stated otherwise.

```powershell
python tools/test_template_hydration.py --root . --json
```

Expected interpretation:

- `tools/test_template_hydration.py` should pass against the generated project.
- Running `python tools/check_placeholders.py .` directly against the master template root may report raw placeholders. Until the checker has a template-root mode, this is expected; the authoritative placeholder check is the generated-project check performed by the smoke test.
- `--root .` means the current directory is the template root.
- `--json` means emit a machine-parseable report instead of only human-readable text.

Optional checks:

```powershell
python tools/verify_official_openspec.py --root .
python tools/enforce_openspec_policy.py --root .
python tools/run_openspec_guard.py --root .
project-background.cmd doctor
git status --short --branch
```

Optional command meaning:

- `tools/verify_official_openspec.py` checks that official OpenSpec-managed files and validation surfaces are present.
- `tools/enforce_openspec_policy.py` checks repository-local OpenSpec policy rules.
- `tools/run_openspec_guard.py` runs the combined guard sequence used by hooks or CI.
- `project-background.cmd doctor` checks the background launcher without intentionally leaving a long-running process active.
- `git status --short --branch` shows whether the target template has a clean Git baseline.

If official OpenSpec bootstrap rewrites managed files, explicitly inspect and commit the drift instead of hiding it.

## 9. Acceptance Criteria

Phase 0 is complete when all of the following are true. As of the 2026-05-25 status refresh, the target template has already satisfied the original Phase 0 Git, hydration, local gate, and local MR helper shape; the remaining current target work is review and commit/publish handling for the later Comet governance patch:

- The bilingual Phase 0 plan pair exists and is aligned.
- The plan pair is registered in the target template registry if that registry is used for implementation plans.
- `.gitignore` covers common local-only runtime, durable-state, dependency, build, and tooling artifacts that should never be committed.
- A template hydration smoke test exists and can generate a test project.
- The generated test project passes placeholder scanning.
- Generated project background entry files exist and are non-empty.
- The smoke test reports launcher limitations honestly and fails on tracebacks, missing files, or fake success.
- Guard help checks run as part of the smoke test or are explicitly recorded as unsupported diagnostics.
- English implementation-plan files remain ASCII-only.
- No user-level Codex skills, plugin caches, or global config files are modified.
- No existing real project repository is modified as part of the target-template patch.
- If the target template is initialized as Git during Phase 0, branch `main` exists and runtime or temporary files are not staged.

The broader production-template upgrade is not complete until later phases also satisfy:

- Default generation works with `core` only.
- Browser and web projects can opt into browser automation and web guidance without making them defaults for all projects.
- Orchestration projects get durable-state and backend-family guidance.
- Publishing profile text matches the selected publishing mode.
- Skills inventory and check tools run without mutating user-level skills.
- The template root has a Git `main` baseline commit after verification.

## 10. Rollback Plan

If Phase 0 causes problems:

1. revert the Phase 0 commit or patch
2. delete only temporary directories created under `.tmp/`
3. do not delete user-level skills or plugin caches
4. do not delete generated real projects unless the user explicitly identifies them as test outputs
5. do not delete or rewrite repo-local `.omx/state` from any real project as part of rollback
6. rerun a clean template hydration smoke test after rollback

## 11. Later Phase Handoff

After Phase 0, later phases may implement:

- profile-aware project generation: `core` for default non-web repositories, `browser` for browser automation work, `web` for frontend and deployment projects, `python-cli` for command-line Python tools, `agent-service` for daemons or workers, `orchestration` for Codex or durable-team repositories, and `full` for temporary broad discovery
- skills governance inventory and profile registry
- browser automation profile preservation for projects such as `D:\PythonProject_OpenClaw` and `D:\PythonProject_CLIProxyAPI`
- JSON output parity across all guard helpers
- publication workflow profiles: `gitlab-first-github-sync`, `github-pr`, and `local-only`
- repo-local durable state isolation defaults for OMX and LangGraph
- generated-project guidance that keeps `native_omx` and `langgraph` as separate durable backend families
- explicit routing guidance that durable team launch is threshold-gated, not automatic at repository startup
