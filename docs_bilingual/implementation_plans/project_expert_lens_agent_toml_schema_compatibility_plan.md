---
doc_id: project_expert_lens_agent_toml_schema_compatibility_plan
lang: en
status: active
plan_readiness: frozen-for-runtime-implementation
doc_class: implementation_plan
created_at: 2026-06-23
updated_at: 2026-06-23
related_docs:
  - docs_bilingual/implementation_plans/project_expert_lens_agent_gui_toolchain_plan.md
  - docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md
---

# Project Expert Lens Agent TOML Schema Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development` when independent slices are available; otherwise use `superpowers:executing-plans`. Keep local-main-first isolation, stop before remote publication, and do not treat expert-lens selection as native-subagent or durable-team evidence.

**Goal:** Fix Codex warnings caused by malformed repo-local native agent TOML while preserving Project Expert Lens GUI behavior for `D:\PythonProject_paper_suggest`.

**Architecture:** Native Codex agent TOML remains schema-compatible and contains only Codex-supported top-level fields. Project Expert Lens metadata remains proven through existing GUI config, target CLI, wrappers, startup hooks, private prompt file, and state paths instead of custom TOML tables.

**Tech Stack:** Python stdlib `tomllib`, Project Expert Lens GUI toolchain, repo-local validation scripts, unittest, PowerShell local gates, Git worktrees, local-main-first integration.

---

## Current status

<!-- CURRENT_STATUS_START -->

- Status: active, frozen for runtime implementation.
- Stage A: this plan pair plus the registry entry is the local-main-first frozen plan package.
- Stage A records the user's decision not to mutate user-level plugin cache; it does not repair vendor/plugin-cache files.
- Stage B: implementation must update B repo source/checkers/tests, classify bundle-managed plugin-cache frontmatter as report-only, and then update `D:\PythonProject_paper_suggest` live artifacts.
- Remote publication: out of scope unless explicitly requested.

<!-- CURRENT_STATUS_END -->

## Problem and decision

Codex rejects unknown top-level fields in native agent role files. The target file `D:\PythonProject_paper_suggest\.codex\agents\thesis-moe-mentor.toml` has valid `name`, `description`, and `developer_instructions`, but also has `[project]`, `[moe]`, `[dispatch]`, and `[extensions]` tables. The first rejected table appears as `unknown field project`.

Decision: remove Project Expert Lens custom metadata from native agent TOML. Do not add a new sidecar file for this fix. Use the already installed `tools/project_moe_gui/project_moe_gui.config.json`, target mode CLI, wrappers, startup hook, `.omx/state/<namespace>/...`, and `MOE.md` to prove Project Expert Lens readiness.

The user also declined editing user-level global plugin cache while this plan was being frozen. Therefore the implementation path must stay repo-local and target-project-local: controlled repo/user/system invalid frontmatter still fails closed, while bundle-managed plugin-cache invalid frontmatter is reported as warning-only until a separate explicit vendor-cache repair approval exists.

## Implementation tasks

<!-- TASK_BACKLOG_START -->

### Task 1: Freeze the implementation plan package

**Files:**
- Create: `docs_bilingual/implementation_plans/project_expert_lens_agent_toml_schema_compatibility_plan.md`
- Create: `docs_bilingual/implementation_plans/project_expert_lens_agent_toml_schema_compatibility_plan.zh-CN.md`
- Modify: `docs_bilingual/docs_registry.yaml`

- [x] Create this bilingual plan pair with `status: active` and `plan_readiness: frozen-for-runtime-implementation`.
- [x] Register the pair in `docs_bilingual/docs_registry.yaml` as an active implementation plan.
- [x] Record that user-level plugin cache must not be mutated by this fix.
- [ ] Run plan validation and local pre-commit/update/archive review.
- [ ] Commit the plan package and merge it into local `main` before runtime implementation starts.

### Task 2: Make Skills frontmatter-resolution plugin-cache-safe

**Files:**
- Modify: `tools/check_skills_audit_frontmatter_resolution.py`
- Modify: `test/check_skills_audit_frontmatter_resolution.test.py`
- Modify if needed: `tools/safety_rule_script_backing_registry.json`

- [ ] Keep repo/user/system skill frontmatter invalid entries fail-closed.
- [ ] Treat bundle-managed plugin-cache invalid frontmatter as report-only warning without editing plugin cache.
- [ ] Prove `edits_plugin_cache=false` in checker output.
- [ ] Add regression coverage for repo/user/system blocking invalid entries and plugin-cache warning-only entries.

### Task 3: Make native agent TOML validation fail closed

**Files:**
- Modify: `tools/check_custom_agent_toml_schema.py`
- Modify: `test/check_custom_agent_toml_schema.test.py`

- [ ] Add an allowlist for native agent top-level keys: `name`, `description`, `developer_instructions`, and `model`.
- [ ] Reject any other top-level key or table, including `project`, `moe`, `dispatch`, and `extensions`.
- [ ] Add a regression test proving a TOML with `[project]` fails.
- [ ] Keep existing required-field and allowed-model tests passing.

### Task 4: Remove custom TOML tables from Project Expert Lens scaffolding and readiness

**Files:**
- Modify: `tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py`
- Modify: `test/project_moe_gui_toolchain.test.py`

- [ ] Update `phase1_agent_toml_template()` so newly scaffolded agent TOML contains only native Codex-compatible fields.
- [ ] Update `inspect_agent_toml()` so it no longer requires `[project]`, `[moe]`, `[dispatch]`, or `[extensions]`.
- [ ] Keep readiness checks for `agent_name`, target config, private prompt boundary, state namespace, mode CLI commands, wrappers, and startup hook.
- [ ] Replace tests that expected extension sections with tests that reject custom TOML tables and accept native-only agent TOML.
- [ ] Bump the GUI toolchain patch version to the next version.

### Task 5: Repair the A project live runtime

**Files:**
- Modify in target project: `D:\PythonProject_paper_suggest\.codex\agents\thesis-moe-mentor.toml`
- Refresh managed GUI artifacts in: `D:\PythonProject_paper_suggest\tools\project_moe_gui\...`

- [ ] Remove `[project]`, `[moe]`, `[dispatch]`, and `[extensions]` from the target agent TOML without changing the role body.
- [ ] Run the updated Project Expert Lens updater/installer against `D:\PythonProject_paper_suggest`.
- [ ] Commit the A project changes and merge them into A project local `main`.
- [ ] Preserve unrelated A project files and report any existing dirty/untracked files separately.

### Task 6: Verify and close

**B repo checks:**
- [ ] `python -m unittest test.check_custom_agent_toml_schema.test` - verifies native agent TOML schema enforcement.
- [ ] `python -m unittest test.project_moe_gui_toolchain.test` - verifies Project Expert Lens scaffold, readiness, and installer compatibility.
- [ ] `python -m unittest test.check_skills_audit_frontmatter_resolution.test` - verifies plugin-cache warning-only handling without user-level cache mutation.
- [ ] `python tools/check_custom_agent_toml_schema.py --root D:\PythonProject_paper_suggest --user-agents-dir D:\PythonProject_paper_suggest\.codex\agents --json` - verifies the real A project agent TOML with the corrected checker.
- [ ] `python tools/check_agent_skill_profile_surface_boundaries.py --root . --json` - verifies the native agent, skill, and profile boundary remains explicit.
- [ ] `python tools/run_openspec_guard.py --root .` - verifies repository governance and OpenSpec guard health.
- [ ] `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1` - verifies the shared local CI gate.
- [ ] `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1` - verifies the local MR review gate before integration.

**A project checks:**
- [ ] Read `thesis-moe-mentor.toml` with `tomllib` and confirm no unknown custom top-level keys remain.
- [ ] `D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json` returns `ok`.
- [ ] `D:\PythonProject_paper_suggest\project-expert-lens-gui.cmd --preflight --json` returns `ok`.
- [ ] `D:\PythonProject_paper_suggest\tools\ci\local_gate.ps1` returns `ok`.
- [ ] A project `HEAD` equals local `main` at the fix commit.

<!-- TASK_BACKLOG_END -->

## Evidence index

<!-- EVIDENCE_INDEX_START -->

- pending: Stage A plan validation, local commit, and local main integration.
- pending: Stage B must make `tools/check_skills_audit_frontmatter_resolution.py` report plugin-cache invalid frontmatter as warning-only while keeping `edits_plugin_cache=false`.
- pending: Stage B source/runtime tests and A project live validation.

<!-- EVIDENCE_INDEX_END -->

## Orchestration and evidence rules

- Use subagents for bounded review/implementation slices when available; close completed agents after fan-in.
- Use durable team only after the plan is frozen and there are at least two independent execution slices. If a backend/tooling blocker exists, record the blocker and let the main session take over.
- Expert timeout, stall, or provider pacing is not result evidence.
- Every local merge must leave rollback evidence through the existing local-main-first helper or equivalent backup ref.
- Do not push GitLab/GitHub or mutate remote refs in this plan.
