---
doc_id: general_templates_cross_project_reuse_upgrade_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/general_templates_cross_project_reuse_upgrade_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/general_templates_cross_project_reuse_upgrade_plan.md
status: active
plan_readiness: ready-for-implementation
doc_class: implementation_plan
last_reviewed: 2026-06-12
target_templates:
  - D:\PythonProject_General
  - D:\PythonProject_General_2
supersedes_or_extends:
  - general_template_phase0_update_patch_plan
  - general_2_local_git_openspec_subagents_only_bootstrap_plan
conflict_priority: Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit
---

# General / General_2 cross-project reuse template upgrade plan zh-CN companion

> This zh-CN companion intentionally uses ASCII-safe wording in this execution batch because the current Windows shell transport corrupted CJK text into question-mark markers. The English canonical file is authoritative for full wording; this companion preserves the same anchors, decisions, task ids, and evidence rows without mojibake markers.

**Goal:** Upgrade `D:\PythonProject_General` and `D:\PythonProject_General_2` for reusable new-project, existing-project, and new-computer bootstrap flows while preserving each template tier boundary.

**Architecture:** `General` is the full capability reusable template. `General_2` is the local-only bootstrap template. This source repository records planning and evidence; each template repository owns its own local Git commit history.

**Tech Stack:** Git worktrees, local-main-first integration, OpenSpec, Comet, Superpowers, gstack governance, harness runtime safety, Spec Kit subordinate/sandbox rules, PowerShell gates, Python checkers, UTF-8 Markdown, hash-redacted R6 receipt contracts.

---

## Current Status

<!-- CURRENT_STATUS_START -->
- 2026-06-12: Plan opened after the user confirmed the two-template reuse upgrade.
- Source repository baseline: `D:\PythonProject_langgraph` local `main` at `d401cf9`, ahead of `gitlab/main` by 49 commits and behind by 0 after fetch.
- `D:\PythonProject_General` baseline: local `main` at `0010af6`; dirty template work exists and must be classified rather than discarded.
- `D:\PythonProject_General_2` baseline: local `main` at `95dc72d`; dirty template work exists and must be classified rather than discarded.
- Native subagent use depends on the active tool contract; the main Codex CLI session remains leader.
- Durable-team adoption is deferred because repo-local `.omx/state/selectors/active.json` points to an existing LangGraph thread and this batch first needs clean write ownership.
<!-- CURRENT_STATUS_END -->

## Scope And Tier Decisions

### `D:\PythonProject_General` full capability template

`General` SHALL carry template-safe surfaces for:

- Comet-controlled OpenSpec/Superpowers workflow governance;
- gstack delivery-loop governance and readiness references;
- harness runtime safety policy and smoke/receipt patterns;
- Spec Kit subordinate governance and sandbox/apply separation;
- user-level wrapper/config installation guidance and smoke surfaces;
- MCP-scope policy and launcher-payload boundary guidance;
- optional `native_omx` and LangGraph readiness profiles with distinct `installed`, `enabled`, `selected`, and `ready` states;
- R6 live-ready/live-executed receipt templates with hash redaction and human-checkable labels.

`General` SHALL NOT carry live `.omx/state/`, selectors, active thread state, session claims, worker mailboxes, runtime logs, credentials, `.env`, browser session state, or remote publication side effects.

### `D:\PythonProject_General_2` local-only bootstrap template

`General_2` SHALL carry only local Git, OpenSpec, Superpowers, Comet, native Codex custom-agent TOML examples, bilingual startup/governance docs, and local JSON gates.

`General_2` SHALL NOT default-enable oh-my-codex, OMX/native_omx, LangGraph, durable teams, `.omx/state/`, user-level wrapper installation, live browser/GUI/WXWork actions, GitLab/GitHub publication, or active remote CI/MR execution.

If remote CI samples are retained, they must be inert examples under template assets, not active root CI files.

## Task Backlog

<!-- TASK_BACKLOG_START -->
### Task 1: Source repository plan registration

**Files:**
- Create: `docs_bilingual/implementation_plans/general_templates_cross_project_reuse_upgrade_plan.md`
- Create: `docs_bilingual/implementation_plans/general_templates_cross_project_reuse_upgrade_plan.zh-CN.md`
- Modify: `docs_bilingual/docs_registry.yaml`

Steps:
1. Create this bilingual umbrella plan with required stable update anchors: `CURRENT_STATUS` records live plan state, `TASK_BACKLOG` records executable work items, and `EVIDENCE_INDEX` records validation and commit evidence.
2. Register the plan pair in `docs_bilingual/docs_registry.yaml`.
3. Validate implementation-plan rules and pre-commit update/archive rules.
4. Commit on an isolated feature branch and integrate to local `main` through the repository helper.

### Task 2: Upgrade `D:\PythonProject_General`

Steps:
1. Create a local feature branch from current template `main` without discarding existing dirty changes.
2. Classify dirty/untracked files into keep, exclude, or repair buckets.
3. Restore `README.md` as a complete full-template entry document and keep the Chinese companion.
4. Ensure `AGENTS.md`, `TEMPLATE_MANIFEST.md`, docs registry, and governance docs describe the full capability tier and conflict priority.
5. Keep template-safe Comet/OpenSpec/Superpowers artifacts and R6 helper surfaces.
6. Add hydration/update guidance for new projects, existing projects, and new computers.
7. Add or repair checks for template-safe R6 receipts, hash-redacted evidence, forbidden live-state copying, and UTF-8/mojibake boundaries.
8. Validate and commit into that template's local `main`.

### Task 3: Upgrade `D:\PythonProject_General_2`

Steps:
1. Create a local feature branch from current template `main` without discarding existing dirty changes.
2. Classify dirty/untracked files into keep, exclude, or repair buckets.
3. Restore `README.md` as a complete local-only bootstrap document.
4. Preserve Comet/OpenSpec/Superpowers/native-subagent guidance while separating it from durable orchestration evidence.
5. Remove active remote CI/MR surfaces or move them to inert optional examples.
6. Harden `tools/check_subagent_only_policy.py` to fail closed on forbidden OMX/LangGraph/live durable state/remote publication surfaces.
7. Validate and commit into that template's local `main`.

### Task 4: Source repository evidence closeout

Steps:
1. Record final `General` and `General_2` commit hashes, validation commands, excluded local artifacts, and rollback branches.
2. Re-run source repository validation.
3. Commit evidence closeout and integrate to local `main`.
4. Stop at the remote-publication gate unless a later user message explicitly requests remote publication.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
| Evidence item | Expected path or command | Status |
| --- | --- | --- |
| Source plan validation | `python .\tools\check_implementation_plan_rules.py --root . --json` | pending |
| Source precommit update/archive check | `python .\tools\check_precommit_update_archive.py --root . --json` | pending |
| Source OpenSpec guard | `python .\tools\run_openspec_guard.py --root .` | pending |
| Source local gate | `.\tools\ci\local_gate.ps1` | pending |
| Source local MR review | `.\tools\ci\local_mr_review.ps1` | pending |
| General validation | `D:\PythonProject_General\tools\ci\local_gate.ps1 -Json` and supporting checkers | pending |
| General_2 validation | `D:\PythonProject_General_2\tools\ci\local_gate.ps1 -Json` and supporting checkers | pending |
| General final commit | `git -C D:\PythonProject_General log -1 --oneline` | pending |
| General_2 final commit | `git -C D:\PythonProject_General_2 log -1 --oneline` | pending |
| Remote publication | explicit later user approval required | not_requested |
<!-- EVIDENCE_INDEX_END -->

## Validation Commands

Use the same validation command blocks as the English canonical plan.

## Rollback And Exclusion Rules

- Preserve existing dirty template changes in backup branches before broad rewrites.
- Exclude `.idea/`, caches, build artifacts, local reports, temporary smoke outputs, and non-template-safe runtime receipts.
- Do not run destructive cleanup against computed paths unless resolved absolute paths are inside the intended target repository.
- Do not mutate remote refs without a fresh explicit remote-publication request.
