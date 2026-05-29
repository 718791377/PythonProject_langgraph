---
doc_id: general_2_local_git_openspec_subagents_only_bootstrap_plan
lang: en
canonical: docs_bilingual/implementation_plans/general_2_local_git_openspec_subagents_only_bootstrap_plan.md
zh_cn_path: docs_bilingual/implementation_plans/general_2_local_git_openspec_subagents_only_bootstrap_plan.zh-CN.md
status: active
plan_readiness: ready-for-implementation
doc_class: implementation_plan
last_reviewed: 2026-05-27
target_template: "D:\PythonProject_General_2"
capability_tier: local-git-openspec-superpowers-native-subagents-only
comet_workflow: full
---

# `D:\PythonProject_General_2` Local Git + OpenSpec + Superpowers + Native Subagents Template Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `comet` as the OpenSpec + Superpowers control layer, then execute this plan one checkbox at a time. Do not add oh-my-codex, native_omx, LangGraph, remote CI/MR, or `.omx/state/` to this template.

**Goal:** Keep `D:\PythonProject_General_2` as the lightweight local template for projects that need local Git, OpenSpec, Superpowers, and native Codex subagents only. The template should be safe for offline/local projects and should not imply durable orchestration or remote publication.

**Architecture:** A local-only repository with bilingual startup docs, OpenSpec skeleton, Comet/Superpowers workflow guidance, paired native agent TOML directories, local-only bootstrap scripts, local gate scripts with remote-compatible JSON shape, and checkers that block forbidden orchestration/runtime surfaces.

**Tech Stack:** Local Git, OpenSpec, Comet, Superpowers, native Codex custom agent TOML, `.codex/agents/`, `template_assets/codex-agents/`, Python checkers, PowerShell local gate, UTF-8 bilingual Markdown.

---

## 0. Review Conclusion

The previous plan correctly excluded oh-my-codex, OMX, LangGraph, remote CI/MR, and `.omx/state/`, but it did not provide enough task-level detail for a future worker. This version turns the local-only boundary into executable slices with file ownership, checks, acceptance criteria, and rollback.

Completeness review:

| Area | Decision | Plan location |
| --- | --- | --- |
| Local-only capability boundary | Complete | Sections 1 and 2 |
| OpenSpec + Superpowers + Comet contract | Complete | Sections 1.2 and 4 |
| Native agent TOML pairing | Complete | Sections 3.2 and 5 Task 3 |
| Local gate JSON compatibility | Complete | Sections 3.4 and 5 Task 5 |
| Forbidden OMX/LangGraph surfaces | Complete | Sections 2.2 and 7 |
| Validation and rollback | Complete | Sections 6 and 8 |

## 1. Relationship Model And Naming Boundary

### 1.1 What this template is

`PythonProject_General_2` is a local-only bootstrap template. It should be used when a new project needs governance and native Codex subagents but does not need remote publication or durable orchestration.

It includes:

- local Git history;
- local OpenSpec artifacts;
- Superpowers and Comet workflow instructions;
- native Codex custom agent TOML files;
- local checkers and local gate helpers;
- bilingual documentation pairs.

### 1.2 What Comet means here

Comet means the OpenSpec + Superpowers workflow:

- OpenSpec owns WHAT;
- Superpowers owns HOW;
- Comet coordinates Open -> Design -> Build -> Verify -> Archive.

Comet is not oh-my-codex, native_omx, LangGraph, a persistent team, or native subagent evidence.

### 1.3 `.codex/agents/` and `template_assets/codex-agents/`

- `.codex/agents/` is the project-local native Codex agent directory that Codex can read at runtime.
- `template_assets/codex-agents/` is the distributable copy used to compare, restore, or install the same agent definitions elsewhere.
- Both directories must contain the same intended TOML files.
- Every standalone custom agent TOML must define top-level `name`, `description`, and `developer_instructions`.

## 2. Goals And Non-Goals

### 2.1 Goals

- Provide a minimal local Git + OpenSpec + Superpowers + Comet governance template.
- Provide native Codex subagent TOML definitions in paired source/distribution directories.
- Provide local-only bootstrap scripts that do not mutate user-level Codex configuration unless a later explicit install command is run.
- Provide local gate scripts with JSON output compatible with the broader repository's gate format, while not adding remote CI/MR configuration.
- Provide UTF-8 bilingual startup summaries and governance docs.
- Provide checkers that fail if oh-my-codex, native_omx, LangGraph, `.omx/state/`, or remote CI/MR files are introduced.

### 2.2 Non-Goals

- Do not configure `origin`, `gitlab`, or `github` remotes by default.
- Do not create `.gitlab-ci.yml`, `.github/workflows/`, GitLab MR helpers, or GitHub PR helpers.
- Do not install or call oh-my-codex, native_omx, OMX durable team, LangGraph, LangGraph CLI wrappers, or `tools/langgraph_durable_orchestrator/`.
- Do not create `.omx/state/`, `.omx/session-claims/`, LangGraph backend JSON, durable selectors, or durable-team receipts.
- Do not copy `C:\Users\lenovo\.codex\config.toml`, tokens, `.env`, credential caches, `.venv/`, `node_modules/`, `.git/`, or live facts from `D:\PythonProject_langgraph`.

## 3. Target Template Topology

Recommended shape:

```text
D:\PythonProject_General_2
|-- AGENTS.md
|-- README.md
|-- TEMPLATE_MANIFEST.md
|-- .gitignore
|-- .codex\agents\
|-- template_assets\codex-agents\
|-- docs_bilingual\
|   |-- project_startup_summary.md
|   |-- project_startup_summary.zh-CN.md
|   |-- docs_registry.yaml
|   `-- governance\
|-- openspec\
|   |-- changes\
|   `-- specs\
`-- tools\
    |-- ci\
    `-- template_checks\
```

### 3.1 Startup docs

Startup summaries must explain local-only scope, read order, OpenSpec/Comet/Superpowers roles, native subagent boundaries, and local gate commands. If a future context-retention sentinel is added, the literal prompt belongs only in the startup summary pair.

### 3.2 Native agent assets

The template should include only intentionally maintained TOML files. Do not copy user-level or unrelated repo-local agents by default. Agent installation to user-level directories, if later added, must be explicit, backed up, and reversible.

### 3.3 OpenSpec assets

Create a local OpenSpec skeleton and an optional sample change. Do not copy this repository's active changes, archived changes, Comet state, or current mainline facts.

### 3.4 Local gate assets

Local gate scripts may use the same JSON report format as remote-capable templates so downstream automation can parse them consistently. This is format compatibility only; it does not enable remote CI/MR.

## 4. Comet / OpenSpec / Superpowers Contract

- Use OpenSpec for local change lifecycle and durable WHAT evidence.
- Use Superpowers for HOW discipline, planning, execution, and verification.
- Use Comet to coordinate phase evidence and archive readiness.
- Keep all Comet/OpenSpec state local to the project and human-readable.
- Do not interpret Comet usage as evidence of native subagent execution or durable orchestration.

## 5. Task-Level Implementation Slices

### Task 0: Target inventory and local-only write scope

**Files:**

- Read: `D:\PythonProject_General_2\AGENTS.md`
- Read: `D:\PythonProject_General_2\README.md`
- Read: `D:\PythonProject_General_2\openspec\`
- Read: `D:\PythonProject_General_2\.codex\agents\`

**Steps:**

- [ ] Confirm whether the target directory already exists.
- [ ] If it is a Git repository, run `git status --short` and stop on uncommitted human changes.
- [ ] Record whether any remotes exist; if remotes exist unexpectedly, report them rather than deleting them.
- [ ] Create a target-local OpenSpec change for the local-only governance bootstrap.
- [ ] Freeze the write scope before editing files.

**Validation:**

- [ ] Target status and blockers are recorded.
- [ ] No remote configuration is added by this task.

### Task 1: Local-only documents and startup authority

**Files:**

- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `TEMPLATE_MANIFEST.md`
- Modify: `docs_bilingual/project_startup_summary.md`
- Modify: `docs_bilingual/project_startup_summary.zh-CN.md`
- Modify: `docs_bilingual/docs_registry.yaml`

**Steps:**

- [ ] State that this template is local Git + OpenSpec + Superpowers + native subagents only.
- [ ] Define read order and task-specific follow-up docs.
- [ ] Explain Comet as OpenSpec + Superpowers control, not durable orchestration.
- [ ] Add forbidden-surface reminders for oh-my-codex, OMX, LangGraph, remote CI/MR, and `.omx/state/`.
- [ ] Register bilingual docs that are expected to stay long-lived.

**Validation:**

- [ ] Bilingual pair checker passes.
- [ ] Docs contain no mojibake or copied live facts.

### Task 2: OpenSpec and Comet local skeleton

**Files:**

- Create/modify: `openspec/config.yaml`
- Create/modify: `openspec/changes/`
- Create/modify: `openspec/specs/`
- Create/modify: `docs_bilingual/governance/openspec_comet_local_workflow.md`
- Create/modify: `docs_bilingual/governance/openspec_comet_local_workflow.zh-CN.md`

**Steps:**

- [ ] Create local OpenSpec directories if missing.
- [ ] Add a template-safe example change or bootstrap note.
- [ ] Document that change history is project-local and not copied from this repository.
- [ ] Document the Comet phase loop and archive criteria.

**Validation:**

- [ ] `openspec validate --all` passes in the target.
- [ ] Example artifacts are clearly marked as template examples.

### Task 3: Native agent TOML pairing

**Files:**

- Modify/create: `.codex/agents/*.toml`
- Modify/create: `template_assets/codex-agents/*.toml`
- Create/modify: `tools/check_custom_agent_toml_schema.py`
- Create/modify: `tools/check_agent_asset_pairs.py`

**Steps:**

- [ ] Select only generic local agents that belong in this template.
- [ ] Keep `.codex/agents/` and `template_assets/codex-agents/` filenames aligned.
- [ ] Verify every TOML has `name`, `description`, and `developer_instructions`.
- [ ] Do not copy missing or unrelated agents from this repository by default.
- [ ] If user-level installation is later supported, require backup before overwrite.

**Validation:**

- [ ] `python .\tools\check_custom_agent_toml_schema.py --root .` passes.
- [ ] Pair checker passes.

### Task 4: Local-only policy checker

**Files:**

- Create/modify: `tools/check_subagent_only_policy.py`
- Create/modify: `tools/check_local_git_only_policy.py`
- Create/modify: `tools/check_template_health.py`
- Create/modify: `.gitignore`

**Steps:**

- [ ] Fail if `.omx/state/` or `.omx/session-claims/` exists in the template.
- [ ] Fail if LangGraph runtime/source files are introduced.
- [ ] Fail if oh-my-codex/native_omx launcher docs are represented as enabled.
- [ ] Fail if remote CI/MR config appears.
- [ ] Ensure `.gitignore` excludes local caches, `.venv/`, `node_modules/`, `.env`, coverage, and temp reports.

**Validation:**

- [ ] `python .\tools\check_subagent_only_policy.py --root .` passes.
- [ ] `python .\tools\check_local_git_only_policy.py --root .` passes.

### Task 5: Local gate with compatible JSON shape

**Files:**

- Create/modify: `tools/ci/local_gate.ps1`
- Create/modify: `tools/ci/local_mr_review.ps1`
- Create/modify: `tools/ci/ci_test_manifest.json` if a manifest is used

**Steps:**

- [ ] Make local gate run template health, subagent-only, TOML schema, bilingual pair, local Git-only, OpenSpec, and `git diff --check`.
- [ ] Make JSON output stable and compatible with the fuller template gate shape.
- [ ] Keep the name `local_mr_review` only as a local review/report helper; do not configure remote MR creation.
- [ ] Document that remote CI/MR is out of scope for this template.

**Validation:**

- [ ] `tools\ci\local_gate.ps1 -Root . -Json` passes.
- [ ] `tools\ci\local_mr_review.ps1 -Root . -Json` passes.

### Task 6: Bootstrap scripts and local Git initialization

**Files:**

- Create/modify: `tools/bootstrap-local-project.ps1`
- Create/modify: `tools/bootstrap-new-pc.ps1`
- Create/modify: `tools/install-subagents-user-level.ps1` if user-level install is supported

**Steps:**

- [ ] Make bootstrap idempotent and parameterized.
- [ ] Use `$env:USERPROFILE` or parameters instead of hard-coded user paths.
- [ ] Run `git init -b main` only in the confirmed target root.
- [ ] Do not add remotes.
- [ ] If committing initial content, do so locally only after validation.

**Validation:**

- [ ] Bootstrap dry-run reports planned actions.
- [ ] Local Git has no default remote after bootstrap.

### Task 7: Source-repository plan maintenance and local integration

**Files:**

- Source repo plan pair under `docs_bilingual/implementation_plans/`
- Target repo files changed by Tasks 0-6

**Steps:**

- [ ] Keep this plan pair aligned with the actual target-template contract.
- [ ] Run source repository implementation-plan and OpenSpec checks.
- [ ] Commit the target repo locally only after target validation.
- [ ] Do not push any remote without explicit remote-publication approval.

**Validation:**

- [ ] Source plan pair passes repository checks.
- [ ] Target repo status is clean after local commit.

## 6. Validation Plan

Run from `D:\PythonProject_General_2`:

```powershell
python .\tools\check_template_health.py --root .
python .\tools\check_subagent_only_policy.py --root .
python .\tools\check_custom_agent_toml_schema.py --root .
python .\tools\check_bilingual_pairs.py --root .
python .\tools\check_local_git_only_policy.py --root .
openspec validate --all
git diff --check
git status --short
```

Run from `D:\PythonProject_langgraph` when maintaining this plan:

```powershell
python .\tools\check_implementation_plan_rules.py --root . --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root . --json
.\tools\ci\local_mr_review.ps1 -Root . -Json
.\tools\ci\local_gate.ps1 -Root . -Json
git diff --check
```

## 7. Acceptance Criteria

- [ ] General_2 remains local Git + OpenSpec + Superpowers + native Codex subagents only.
- [ ] `.codex/agents/` and `template_assets/codex-agents/` stay paired.
- [ ] Every agent TOML has `name`, `description`, and `developer_instructions`.
- [ ] No `.omx/state/`, `.omx/session-claims/`, LangGraph, oh-my-codex, native_omx, remote CI, or remote MR/PR config exists.
- [ ] Local gates emit stable JSON and do not require a remote.
- [ ] Chinese and English docs are paired and UTF-8 clean.

## 8. Rollback And Cleanup

- Rename a bad target directory to `D:\PythonProject_General_2.backup.<timestamp>` before manual cleanup.
- Revert document or checker mistakes with target-local Git.
- Restore user-level agent files from `%USERPROFILE%\.codex\agents.backup.<timestamp>\` if an explicit install script was run.
- Delete `.git/` only manually after confirming no commits need to be kept.
- Recover OpenSpec files by inspecting `git status --short` and reverting listed files, not by automatically clearing `openspec/`.
- Do not use cleanup scripts that recursively delete outside the confirmed target root.

## 9. Risks And Default Decisions

- Risk: local-only template accidentally gains durable orchestration. Default: fail closed through `check_subagent_only_policy.py`.
- Risk: agent TOML surfaces drift between runtime and template assets. Default: pair checker must compare filenames and required schema.
- Risk: remote CI/MR language appears because gate JSON is compatible. Default: docs state JSON compatibility is format-only.
- Risk: copied terminal output corrupts Chinese docs. Default: write UTF-8 files directly and check source text.
- Risk: user-level agent install overwrites existing files. Default: no install by default; explicit install requires backup.

## 10. Self-Check Checklist

- [ ] No oh-my-codex, OMX, LangGraph, remote CI/MR, or `.omx/state/` surfaces are enabled.
- [ ] OpenSpec and Comet are local governance only.
- [ ] Native agent TOML files are paired and schema-valid.
- [ ] Local gates and checkers have exact commands.
- [ ] Rollback never deletes Git history automatically.
- [ ] Source and target repositories remain separate.
