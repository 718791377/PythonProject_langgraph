---
doc_id: general_template_phase0_update_patch_plan
lang: en
canonical: docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md
status: active
doc_class: implementation_plan
created_at: 2026-04-25
phase: 0
---

# D:\PythonProject_General Phase 0 Template Update Patch Plan

> Cold-start contract: this plan is self-contained. A new Codex session with no prior chat context can read this file, `README.md`, `AGENTS.md`, `project_startup_summary.md`, and `docs_bilingual/governance/template_completion_protocol.md`, then implement the Phase 0 patch safely.

## Bilingual Alignment Status

- English ASCII file: this file is the implementation source of truth.
- Chinese companion: `docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.zh-CN.md`.
- Alignment rule: keep both files synchronized for scope, safety rules, deliverables, validation commands, and acceptance criteria.
- Current finding: Phase 0 is a safety and testability patch for the master template root, not a full profile or skills-governance rollout.
- Name clarity rule: every listed script, path, command, variable, or profile name must be followed by a short explanation so a cold-start reader can tell what it is for.

## 1. Goal

Create a small, reviewable Phase 0 patch for `D:\PythonProject_General` so the template itself becomes safer to maintain before larger profile, skills, browser, web, or orchestration features are added.

The patch should make the template easier to verify in three states:

1. the master template root `D:\PythonProject_General`
2. a freshly generated project created by `new-openspec-project.ps1`
3. a no-context Codex session that only knows the generated repository files

## 2. Current Observed State

As of 2026-04-25, the template root contains:

- OpenSpec bilingual repository starter files
- `AGENTS.md` - the repository-level operating contract for Codex sessions.
- startup summaries in English and Chinese
- OpenSpec governance docs and `strict-governance` schema files - the policy documents and schema gates that define the repository's structured-change workflow.
- GitHub Actions and GitLab CI guard surfaces
- git hook templates
- `new-openspec-project.ps1` - the PowerShell generator that copies and hydrates this template into a new project.
- Windows Explorer and PyCharm launcher helpers - optional UI entry points that call the same project generator.
- root background-process launchers: `project-background.cmd`, `project-background.ps1`, and `project-background.json` - the default command wrappers and configuration for starting, checking, and stopping a project-local long-running process.
- `tools/project_background.py` - the Python supervisor used by the background-process launchers.
- `tools/background_keepalive.py` - the harmless default process used to prove background persistence before a real server or daemon exists.
- OpenSpec verification and enforcement helpers

Important findings:

- The master template root is not currently a git repository.
- The master template root intentionally contains raw placeholders for generated repositories.
- A generated test project should have no unresolved placeholders after hydration.
- Background-process support exists and should be smoke-tested in generated projects.
- The template root `.gitignore` is too small for Python, Node, OpenSpec, Codex, and local runtime work.

## 3. Phase 0 Scope

Phase 0 is limited to template maintainability and safety.

In scope:

1. Add or update documentation for the Phase 0 patch plan.
2. Register this implementation plan in `docs_bilingual/docs_registry.yaml`.
3. Add a stronger template-root `.gitignore` for local-only runtime and tool artifacts.
4. Add a template hydration smoke-test script that creates a temporary generated project and verifies the generated project, not the master template root, is free of unresolved placeholders.
5. Document the difference between master-template placeholders and generated-project placeholders.
6. Verify root background entry points in generated-project smoke tests.
7. Keep all changes small enough for a focused review.

Out of scope for Phase 0:

- implementing profile-aware project generation
- implementing skills inventory or skills governance checks
- deleting, disabling, or moving user-level skills
- changing `C:\Users\lenovo\.codex\config.toml`, which is the user-level Codex configuration file outside this repository.
- changing Vercel, GitHub, browser, or OpenSpec plugin installations
- changing real project repositories such as `D:\PythonProject_OpenClaw`, `D:\PythonProject_CLIProxyAPI`, `D:\project`, or `D:\PythonProject_langgraph`
- requiring a GitLab or GitHub remote for the template root
- redesigning `strict-governance`, which is the repository-local OpenSpec schema used for review and approval gates.

## 4. Safety Rules

1. Do not edit generated child projects except inside temporary test directories created for smoke tests.
2. Do not delete user-level Codex skills or plugin cache entries.
3. Do not modify global Codex, Git, npm, Python, or PowerShell configuration.
4. Do not assume the master template root should pass placeholder checks; only generated projects should pass placeholder checks.
5. Do not start long-running background processes without stopping them or confining them to `.project-runtime/`.
6. Do not introduce project-specific facts from `D:\PythonProject_langgraph` into the general template.
7. Keep English implementation-plan files ASCII-only.
8. Keep Chinese companion files registered and updated with the English source.

## 5. Deliverables

### 5.1 Documentation

Create and maintain:

- `docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md` - the English ASCII Phase 0 implementation source of truth.
- `docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.zh-CN.md` - the Chinese companion that explains the same implementation scope and safety rules.

Update:

- `docs_bilingual/docs_registry.yaml` - the document index that makes the plan discoverable to cold-start sessions and validation scripts.

Optional documentation updates if the implementation patch touches the related surface:

- `README.md` - the English template overview and operator-facing usage entry.
- `README.zh-CN.md` - the Chinese template overview and operator-facing usage entry.
- `docs_bilingual/governance/template_completion_protocol.md` - the English policy for replacing template defaults with real project facts.
- `docs_bilingual/governance/template_completion_protocol.zh-CN.md` - the Chinese companion for the template completion policy.

### 5.2 Template Ignore Rules

Update `.gitignore` to ignore at least:

```gitignore
.omx/
.tmp/
__pycache__/
*.pyc
.pytest_cache/
.venv/
node_modules/
openspec-guard-report.json
.project-runtime/
```

Ignore entry meaning:

- `.omx/` - repository-local durable orchestration state that should not be committed.
- `.tmp/` - scratch space for template hydration tests and other temporary outputs.
- `__pycache__/` and `*.pyc` - Python bytecode caches generated by local runs.
- `.pytest_cache/` - pytest's local test-result cache.
- `.venv/` - a project-local Python virtual environment.
- `node_modules/` - Node.js dependency installs.
- `openspec-guard-report.json` - local or CI guard report output.
- `.project-runtime/` - local background-process pid, log, and heartbeat state.

### 5.3 Template Hydration Smoke Test

Add a script such as:

- `tools/test_template_hydration.py` - the proposed smoke-test runner that generates a temporary project and verifies the generated output.

Minimum behavior:

1. locate the master template root
2. create a temporary output directory under `.tmp/`, which is the template-local scratch area ignored by git
3. run `new-openspec-project.ps1 -ProjectName TemplateSmokeTest -DestinationRoot <temp> -SkipOfficialOpenSpecBootstrap`, which creates a generated project without refreshing official OpenSpec managed files
4. run `python tools/check_placeholders.py .` inside the generated project, which verifies that hydration replaced raw template placeholders
5. assert `tools/project_background.py` exists and is non-empty inside the generated project, because the background supervisor must be copied into every new project
6. run `project-background.cmd doctor` or a safe equivalent, which checks the background launcher without leaving a long-running process active
7. clean up temporary output unless `--keep-temp` is provided; `--keep-temp` should preserve the generated project for debugging failed smoke tests
8. return a non-zero exit code on failure
9. support `--json` for machine-readable output that CI jobs and Codex sessions can parse

Recommended command:

```powershell
python tools/test_template_hydration.py --root . --json
```

This command runs the template hydration smoke test against the current template root and emits a JSON report.

### 5.4 Guard Surface Compatibility Notes

Phase 0 should record, but not necessarily fix, differences between this template and `D:\PythonProject_langgraph` guard helper capabilities.

Known difference to inspect later:

- some `D:\PythonProject_langgraph` helper scripts support `--json`
- some `D:\PythonProject_General` helper scripts currently do not support `--json`

Phase 0 may add the inventory note; a later phase can add JSON output consistently.

## 6. Implementation Steps

1. Create `docs_bilingual/implementation_plans/` if missing; this directory stores implementation plans that are not OpenSpec change artifacts.
2. Add the English and Chinese Phase 0 plan files.
3. Add the plan pair to `docs_bilingual/docs_registry.yaml`, which is the bilingual document registry.
4. Update `.gitignore` with local runtime and tool artifacts so generated logs, caches, and scratch directories do not become commits.
5. Add `tools/test_template_hydration.py`, the smoke-test runner for generated-project hydration.
6. Run the template hydration smoke test.
7. Run targeted checks against the new plan files:
   - English file has zero non-ASCII characters.
   - Both files have no trailing whitespace.
   - Both files are registered in `docs_bilingual/docs_registry.yaml`, the registry used by documentation checks.
8. Run the existing generated-project placeholder check through the smoke test.
9. If the template root is initialized as a git repository, commit the Phase 0 patch on a feature branch.

## 7. Validation Commands

Run from `D:\PythonProject_General` unless stated otherwise.

```powershell
python tools/test_template_hydration.py --root . --json
python tools/check_placeholders.py .
```

Expected interpretation:

- `tools/test_template_hydration.py` should pass for the generated project.
- `tools/check_placeholders.py .` at the master template root may report raw placeholders; this is expected until the checker has a template-root mode or until the command is scoped to generated projects.
- `--root .` means "use the current directory as the template root".
- `--json` means "emit a machine-readable report instead of only human-readable text".

Optional checks:

```powershell
python tools/verify_official_openspec.py --root .
python tools/enforce_openspec_policy.py --root .
python tools/run_openspec_guard.py --root .
```

Optional command meaning:

- `tools/verify_official_openspec.py` checks that official OpenSpec-managed files and validation surfaces are present.
- `tools/enforce_openspec_policy.py` checks repository-local OpenSpec policy rules.
- `tools/run_openspec_guard.py` runs the combined guard sequence used by hooks or CI.

If the official OpenSpec bootstrap mutates managed files, inspect and commit those managed files intentionally rather than hiding the drift.

## 8. Acceptance Criteria

Phase 0 is complete when all of the following are true:

- the bilingual Phase 0 plan pair exists
- the plan pair is registered in `docs_bilingual/docs_registry.yaml`, which lets documentation checks find both language versions
- `.gitignore` covers common local-only runtime and tooling artifacts that should never be committed
- a template hydration smoke test exists and can generate a test project
- the generated test project passes placeholder scanning
- generated project background entry files exist and are non-empty
- English implementation-plan files remain ASCII-only
- no user-level Codex skills, plugin caches, or global config files are modified
- no existing real project repository is modified

## 9. Rollback Plan

If Phase 0 causes problems:

1. revert the Phase 0 commit or patch
2. delete only temporary directories created under `.tmp/`
3. do not delete user-level skills or plugin caches
4. do not delete generated real projects unless the user explicitly identifies them as test outputs
5. rerun a clean template hydration smoke test after rollback

## 10. Later Phase Handoff

After Phase 0, later phases may implement:

- profile-aware project generation: `core` for default non-web repositories, `browser` for browser automation work, `web` for frontend and deployment projects, `python-cli` for command-line Python tools, `agent-service` for daemons or workers, `orchestration` for Codex or durable-team repositories, and `full` for temporary broad discovery
- skills governance inventory and profile registry
- browser automation profile preservation for projects such as `D:\PythonProject_OpenClaw` and `D:\PythonProject_CLIProxyAPI`
- JSON output parity across all guard helpers
- publication workflow profiles: GitLab-first, GitHub-PR, and local-only
- repo-local durable state isolation defaults for OMX and LangGraph
