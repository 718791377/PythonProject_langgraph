---
doc_id: general_templates_cross_project_reuse_upgrade_plan
lang: en
canonical: docs_bilingual/implementation_plans/general_templates_cross_project_reuse_upgrade_plan.md
zh_cn_path: docs_bilingual/implementation_plans/general_templates_cross_project_reuse_upgrade_plan.zh-CN.md
status: active
plan_readiness: implemented-local-main
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

# General / General_2 Cross-Project Reuse Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `comet` as the OpenSpec + Superpowers control layer, then use `superpowers:executing-plans` or `superpowers:subagent-driven-development` when the runtime explicitly allows subagents. Keep the current Codex CLI session as leader. Do not mutate remote refs. Do not copy live durable state, credentials, or machine-local runtime evidence into templates.

**Goal:** Upgrade `D:\PythonProject_General` and `D:\PythonProject_General_2` so existing and new projects, including projects on a new computer, can reuse as much of this repository's Codex/OpenSpec/Comet/gstack/harness/Spec Kit governance as each template tier safely permits.

**Architecture:** `General` is the full reusable capability template with optional user-level wrapper/config guidance and checker-backed readiness surfaces. `General_2` is the local-only bootstrap template limited to local Git, OpenSpec, Superpowers, Comet, and native Codex subagent TOMLs. This repository records the implementation plan, evidence, and final template commits, while each template repository owns its own local Git history.

**Tech Stack:** Git worktrees, local-main-first integration, OpenSpec, Comet, Superpowers, gstack governance docs, harness runtime safety policy, Spec Kit subordinate/sandbox rules, PowerShell local gates, Python checkers, UTF-8 bilingual Markdown, hash-redacted R6 receipt contracts.

---

## Current Status

<!-- CURRENT_STATUS_START -->
- 2026-06-12: Plan registration completed and merged into source local `main` at `f3c2900` (source plan registration commit).
- 2026-06-12: `D:\PythonProject_General` completed and merged into its local `main` at `a814883` (General full-template upgrade commit); rollback ref: `refs/backup/local-main/20260612-before-upgrade-general-full-template` -> `0010af6`.
- 2026-06-12: `D:\PythonProject_General_2` completed and merged into its local `main` at `8dea3e6` (General_2 local-only template upgrade commit); rollback ref: `refs/backup/local-main/20260612-before-upgrade-general2-local-template` -> `95dc72d`.
- 2026-06-12: General_2 keeps active Comet/OpenSpec/Superpowers/native-subagent surfaces but moved remote CI and R6 examples to inert samples under `template_assets/inert-samples/`.
- 2026-06-12: Evidence closeout is now in source branch `close-general-templates-evidence-20260612`; source local `main` is ahead of `gitlab/main` by 50 and behind by 0 after fetch.
- Native subagent spawning was not used because the active tool contract does not expose native `spawn_agent`; previous read-only expert findings were absorbed and main-session execution remained authoritative.
- Durable team adoption remained not selected because the closeout collapsed to single-slice template/evidence work after the plan was frozen.
<!-- CURRENT_STATUS_END -->

## Scope And Template Tier Decisions

### `D:\PythonProject_General` full capability template

`General` SHALL include reusable template-safe surfaces for:

- Comet-controlled OpenSpec/Superpowers workflow governance;
- gstack delivery-loop governance and plan/readiness references;
- harness runtime safety policy and smoke/receipt patterns;
- Spec Kit subordinate governance and sandbox/apply separation;
- user-level wrapper/config installation guidance and smoke scripts;
- MCP-scope policy and launcher-payload boundary guidance;
- optional `native_omx` and LangGraph readiness profiles that distinguish `installed`, `enabled`, `selected`, and `ready`;
- R6 live-ready/live-executed receipt templates using hash redaction plus human-checkable labels.

`General` SHALL NOT include:

- this repository's `.omx/state/`, selectors, active LangGraph thread state, session claims, worker mailboxes, runtime logs, or receipts containing sensitive live payloads;
- credentials, `.env`, global user config, browser/GUI session state, or machine-local absolute facts except documented examples;
- remote publication side effects.

### `D:\PythonProject_General_2` local-only bootstrap template

`General_2` SHALL include only:

- local Git bootstrap and health-check commands;
- OpenSpec + Superpowers + Comet workflow instructions;
- native Codex custom-agent TOML examples and local checker coverage;
- bilingual startup/governance docs;
- local gate scripts with machine-readable JSON output.

`General_2` SHALL NOT default-enable:

- oh-my-codex, OMX/native_omx, LangGraph, durable teams, `.omx/state/`, user-level wrapper installation, live browser/GUI/WXWork actions, GitLab/GitHub publication, or remote CI/MR execution.

If remote CI samples are useful, they must be inert examples under a template-assets path and must not exist as active root `.gitlab-ci.yml` or `.github/workflows/*` files in the local-only template.

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
4. Commit on an isolated feature branch and integrate to local `main` through the repository's local-main-first helper.

### Task 2: Upgrade `D:\PythonProject_General`

**Owned repository:** `D:\PythonProject_General`

Steps:
1. Create a local feature branch from current template `main` without discarding existing dirty changes.
2. Classify dirty/untracked files into keep, exclude, or repair buckets.
3. Restore `README.md` as a complete full-template entry document; keep `README.zh-CN.md` as the Chinese companion.
4. Ensure `AGENTS.md`, `TEMPLATE_MANIFEST.md`, docs registry, and governance docs describe the full capability tier and conflict priority.
5. Keep Comet/OpenSpec/Superpowers artifacts and R6 receipt/runtime helper surfaces that are template-safe.
6. Add hydration/update guidance for new projects, existing projects, and new computers.
7. Add or repair checks for template-safe R6 receipts, hash-redacted sensitive evidence, forbidden live-state copying, and UTF-8/mojibake boundaries.
8. Run local template validation and commit the finished template branch into its local `main`.

### Task 3: Upgrade `D:\PythonProject_General_2`

**Owned repository:** `D:\PythonProject_General_2`

Steps:
1. Create a local feature branch from current template `main` without discarding existing dirty changes.
2. Classify dirty/untracked files into keep, exclude, or repair buckets.
3. Restore `README.md` as a complete local-only bootstrap document.
4. Preserve Comet/OpenSpec/Superpowers/native-subagent guidance but keep it separate from durable orchestration evidence.
5. Remove active remote CI/MR surfaces or move them to inert optional examples.
6. Harden `tools/check_subagent_only_policy.py` so forbidden OMX/LangGraph/live durable state/remote publication surfaces fail closed.
7. Run local-only template validation and commit the finished template branch into its local `main`.

### Task 4: Source repository evidence closeout

**Files:**
- Modify: this plan pair
- Modify: `docs_bilingual/docs_registry.yaml` only if registry metadata needs final evidence notes

Steps:
1. Record final `General` and `General_2` commit hashes, validation commands, excluded local artifacts, and rollback branches.
2. Re-run source repository validation.
3. Commit evidence closeout and integrate through local-main-first flow.
4. Stop at the remote-publication gate unless a later user message explicitly requests remote push/publication.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
| Evidence item | Expected path or command | Status |
| --- | --- | --- |
| Source plan registration commit | `git log -1 --oneline` after Task 1 local integration | `f3c2900 source plan registration commit` |
| Source remote-base check before closeout | `git fetch gitlab`; `git rev-list --left-right --count main...gitlab/main` | `50 0` before closeout branch creation |
| Source ownership precheck | `python tools/check_session_ownership_claims.py --root . --precheck-task "general templates evidence closeout" --target-path "docs_bilingual/implementation_plans/general_templates_cross_project_reuse_upgrade_plan.md" --json` | `ok=true`, target path unclaimed |
| General validation | `powershell -NoProfile -ExecutionPolicy Bypass -File D:\PythonProject_General\tools\ci\local_gate.ps1 -Root D:\PythonProject_General -Json` | passed at `2026-06-12T02:45:08Z`; includes hydration, OpenSpec policy, Comet policy, and R6 receipt checker |
| General final commit | `git -C D:\PythonProject_General log -1 --oneline` | `a814883 General full-template upgrade commit` |
| General rollback ref | `git -C D:\PythonProject_General rev-parse refs/backup/local-main/20260612-before-upgrade-general-full-template` | `0010af632587fc6fd0cb792905f66447dedefbc6` |
| General_2 validation | `powershell -NoProfile -ExecutionPolicy Bypass -File D:\PythonProject_General_2\tools\ci\local_gate.ps1 -Root D:\PythonProject_General_2 -Json -RequireCleanGit` | passed at `2026-06-12T02:45:06Z`; includes template health, ownership, subagent-only, OpenSpec, bilingual, name-clarity, local-only, Comet policy, and clean git |
| General_2 local MR review | `powershell -NoProfile -ExecutionPolicy Bypass -File D:\PythonProject_General_2\tools\ci\local_mr_review.ps1 -Root D:\PythonProject_General_2 -BaseRef main -HeadRef HEAD -Json` | passed before local `main` merge; helper fixed to report `changed_files` correctly |
| General_2 final commit | `git -C D:\PythonProject_General_2 log -1 --oneline` | `8dea3e6 General_2 local-only template upgrade commit` |
| General_2 rollback ref | `git -C D:\PythonProject_General_2 rev-parse refs/backup/local-main/20260612-before-upgrade-general2-local-template` | `95dc72d0cc039659935865d2c6377e288773dbb5` |
| Excluded or inert artifacts | template policy and checker evidence | `.idea/`, live `.omx/state/`, credentials, browser/GUI/WXWork state, remote publication state, active General_2 root CI, and active General_2 R6 runtime helper files excluded; General_2 remote CI/R6 kept only as inert samples |
| Source plan validation | `python .\tools\check_implementation_plan_rules.py --root . --json` | passed at `2026-06-12T03:00:28Z` with legacy warnings only |
| Source precommit update/archive check | `python .\tools\check_precommit_update_archive.py --root . --json` | passed at `2026-06-12T03:00:28Z`; changed paths limited to the plan pair |
| Source OpenSpec guard | `python .\tools\run_openspec_guard.py --root .` | passed at `2026-06-12T03:01:39Z` with existing legacy warnings only |
| Source local gate | `.\tools\ci\local_gate.ps1` | to run in evidence closeout branch before integration |
| Source local MR review | `.\tools\ci\local_mr_review.ps1` | to run after evidence closeout commit |
| Remote publication | explicit later user approval required | not_requested |
<!-- EVIDENCE_INDEX_END -->

## Validation Commands

Run in `D:\PythonProject_langgraph` feature worktree before source-repo commits:

```powershell
python .\tools\check_implementation_plan_rules.py --root . --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root .
.\tools\ci\local_gate.ps1
.\tools\ci\local_mr_review.ps1
git diff --check
```

Run in `D:\PythonProject_General` before committing that template:

```powershell
openspec list --json
openspec validate --all
.\tools\ci\local_gate.ps1 -Json
python .\tools\check_openspec_comet_superpowers_policy.py --root . --json
python .\tools\check_r6_live_runtime_receipts.py --root . --json
git diff --check
```

Run in `D:\PythonProject_General_2` before committing that template:

```powershell
openspec validate --all
.\tools\ci\local_gate.ps1 -Json
python .\tools\check_subagent_only_policy.py --root . --json
python .\tools\check_openspec_comet_superpowers_policy.py --root . --json
python .\tools\check_r6_live_runtime_receipts.py --root . --json
git diff --check
```

## Rollback And Exclusion Rules

- Preserve existing dirty template changes in backup branches before broad rewrites.
- Exclude `.idea/`, caches, build artifacts, local reports, temporary smoke outputs, and runtime receipts that are not template-safe.
- Do not run destructive cleanup against computed paths unless resolved absolute paths are inside the intended target repository.
- Do not push, create MR/PR, sync GitHub, or mutate any remote ref without a fresh explicit remote-publication request.
