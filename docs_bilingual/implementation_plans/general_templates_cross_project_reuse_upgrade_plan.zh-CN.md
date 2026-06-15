---
doc_id: general_templates_cross_project_reuse_upgrade_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/general_templates_cross_project_reuse_upgrade_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/general_templates_cross_project_reuse_upgrade_plan.md
status: active
plan_readiness: active-implementation
doc_class: implementation_plan
last_reviewed: 2026-06-15
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
- 2026-06-12: Plan registration completed and merged into source local `main` at `f3c2900`.
- 2026-06-12: `D:\PythonProject_General` completed and merged into local `main` at `a814883`; rollback ref `refs/backup/local-main/20260612-before-upgrade-general-full-template` points to `0010af6`.
- 2026-06-12: `D:\PythonProject_General_2` completed and merged into local `main` at `8dea3e6`; rollback ref `refs/backup/local-main/20260612-before-upgrade-general2-local-template` points to `95dc72d`.
- 2026-06-12: General_2 keeps Comet/OpenSpec/Superpowers/native-subagent surfaces active but keeps remote CI and R6 examples inert under `template_assets/inert-samples/`.
- 2026-06-12: Source evidence closeout merged into local `main` at `b67b94f`; rollback ref `refs/backup/local-main/20260612-113345-before-close-general-templates-evidence-20260612` points to `f3c2900`; feature worktree and branch were cleaned by the guarded helper.
- 2026-06-12: Completion audit revalidated `D:\PythonProject_General` and `D:\PythonProject_General_2` current local `main` gates at `2026-06-12T04:02Z`; both gates passed and both template worktrees are clean.
- Native subagent spawning was blocked by the active platform tool contract, so the main Codex CLI session remained leader.
- Durable-team adoption stayed not selected because closeout work is a single evidence/documentation slice after plan freeze.
- 2026-06-15: Incremental template refresh opened from source local `main` at `802e458` after `git fetch gitlab` confirmed local `main` is ahead 87 and behind 0 against `gitlab/main`; `D:\PythonProject_General` was clean at `4a7d858`, and `D:\PythonProject_General_2` was clean at `1952f6d`.
- 2026-06-15: Safe incremental sync scope is limited to reusable template surfaces from `b67b94f..802e458`: single-panel conversation surface, full-field `Routing trace` contract, reusable document/PDF/vector-tool promotion, recent manual workflow packaging, fresh-source extraction guidance, and governance wording that remains template-safe.
- 2026-06-15: Excluded from templates: Skills-audit memory rollups, Project MOE GUI implementation specifics, WXWork/browser/GUI live-state evidence, `.omx/state/`, session claims, credentials, sensitive runtime receipts, remote publication state, and repository-specific LangGraph durable state.
- 2026-06-15: Source `docs_bilingual/docs_registry.yaml` indentation repair is included in this plan refresh because the newly registered `reusable_document_pdf_vector_tools_promotion_plan` entry was outside the `documents` list and broke YAML parsing.
- 2026-06-15: `D:\PythonProject_General` revalidated on local `main` at `d2d5a27`; rollback ref `refs/backup/local-main/20260615-before-general-safe-increment` -> `4a7d85890cf10f7d22d88836fc3ee8f5edbd2eb1`; local gate and local MR review passed.
- 2026-06-15: `D:\PythonProject_General_2` revalidated on local `main` at `101025b`; rollback ref `refs/backup/local-main/20260615-before-general2-safe-increment` -> `1952f6dda40c9e52c8ced4325aee1ffc407eea67`; local gate and local MR review passed.
- 2026-06-15: Source `main` was re-fetched against `gitlab/main` and remains ahead 97 / behind 0 before final source closeout.
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

### Task 5: 2026-06-15 source plan refresh and registry repair

**Files:**
- Modify: `docs_bilingual/implementation_plans/general_templates_cross_project_reuse_upgrade_plan.md`
- Modify: `docs_bilingual/implementation_plans/general_templates_cross_project_reuse_upgrade_plan.zh-CN.md`
- Modify: `docs_bilingual/docs_registry.yaml`

Steps:
1. Record the 2026-06-15 safe incremental sync scope and template tier decisions in this plan pair.
2. Repair `docs_bilingual/docs_registry.yaml` so `reusable_document_pdf_vector_tools_promotion_plan` remains under the top-level `documents` list.
3. Validate implementation-plan, pre-commit update/archive, OpenSpec guard, and diff whitespace checks.
4. Commit the source plan refresh on an isolated branch and integrate it into local `main` before template mutation.

### Task 6: 2026-06-15 update `D:\PythonProject_General`

**Owned repository:** `D:\PythonProject_General`

Steps:
1. Create a local template feature branch from clean `main` at `4a7d858` and preserve a rollback ref.
2. Add template-safe governance for single-panel `Updated Plan` rendering and full-field `Routing trace` output without duplicating native CLI plan panels.
3. Add reusable docs/tooling guidance for recent workflow packaging, fresh-source extraction, and document/PDF/vector tool promotion without copying source-repo live evidence.
4. Refresh `AGENTS.md`, `README.md`, `TEMPLATE_MANIFEST.md`, docs registry, and local gate surfaces as needed.
5. Validate the full template with local gate, conversation surface, OpenSpec/Comet/Superpowers, R6 receipt, and diff checks.
6. Commit and fast-forward merge the template branch into `D:\PythonProject_General` local `main`.

### Task 7: 2026-06-15 update `D:\PythonProject_General_2`

**Owned repository:** `D:\PythonProject_General_2`

Steps:
1. Create a local template feature branch from clean `main` at `1952f6d` and preserve a rollback ref.
2. Sync only the local-only subset of conversation surface and reusable workflow guidance.
3. Keep oh-my-codex, OMX/native_omx, LangGraph, durable teams, `.omx/state`, user-level wrapper installation, live browser/GUI/WXWork actions, active R6 runtime, GitLab/GitHub publication, and active remote CI/MR surfaces disabled by default.
4. Keep optional remote/R6 examples inert under `template_assets/inert-samples/` only.
5. Validate with local-only, subagent-only, OpenSpec/Comet/Superpowers, conversation surface, bilingual pair, and clean-git checks.
6. Commit and fast-forward merge the template branch into `D:\PythonProject_General_2` local `main`.

### Task 8: 2026-06-15 source evidence closeout

**Files:**
- Modify: this plan pair

Steps:
1. Record final 2026-06-15 source, General, and General_2 commits plus rollback refs and validation commands.
2. Confirm template exclusions remain intact and no live state was copied.
3. Re-run source validation, commit evidence closeout, and integrate through the local-main-first helper.
4. Stop at the remote-publication gate.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
| Evidence item | Expected path or command | Status |
| --- | --- | --- |
| Source plan registration commit | `git log -1 --oneline` after Task 1 local integration | `f3c2900` |
| Source remote-base check before closeout | `git fetch gitlab`; `git rev-list --left-right --count main...gitlab/main` | `50 0` |
| Source ownership precheck | `python tools/check_session_ownership_claims.py --root . --precheck-task "general templates evidence closeout" --target-path "docs_bilingual/implementation_plans/general_templates_cross_project_reuse_upgrade_plan.md" --json` | `ok=true`, target path unclaimed |
| General 2026-06-12 validation | `powershell -NoProfile -ExecutionPolicy Bypass -File D:\PythonProject_General\tools\ci\local_gate.ps1 -Root D:\PythonProject_General -Json` | passed at `2026-06-12T04:02:36Z`; current `main` is `a814883`; key template files present; `.omx/state` absent |
| General 2026-06-12 final commit | `git -C D:\PythonProject_General log -1 --oneline` | `a814883` |
| General 2026-06-12 rollback ref | `git -C D:\PythonProject_General rev-parse refs/backup/local-main/20260612-before-upgrade-general-full-template` | `0010af632587fc6fd0cb792905f66447dedefbc6` |
| General_2 2026-06-12 validation | `powershell -NoProfile -ExecutionPolicy Bypass -File D:\PythonProject_General_2\tools\ci\local_gate.ps1 -Root D:\PythonProject_General_2 -Json -RequireCleanGit` | passed at `2026-06-12T04:02:34Z`; current `main` is `8dea3e6`; clean git; root remote CI absent; inert samples present; `.omx/state` absent |
| General_2 local MR review | `powershell -NoProfile -ExecutionPolicy Bypass -File D:\PythonProject_General_2\tools\ci\local_mr_review.ps1 -Root D:\PythonProject_General_2 -BaseRef main -HeadRef HEAD -Json` | passed before local `main` merge; changed-files output repaired |
| General_2 2026-06-12 final commit | `git -C D:\PythonProject_General_2 log -1 --oneline` | `8dea3e6` |
| General_2 2026-06-12 rollback ref | `git -C D:\PythonProject_General_2 rev-parse refs/backup/local-main/20260612-before-upgrade-general2-local-template` | `95dc72d0cc039659935865d2c6377e288773dbb5` |
| Excluded or inert artifacts | template policy and checker evidence | live `.omx/state/`, credentials, browser/GUI/WXWork state, remote publication state, active General_2 root CI, and active General_2 R6 runtime helpers excluded; General_2 remote CI/R6 only inert samples |
| Source plan validation | `python .\tools\check_implementation_plan_rules.py --root . --json` | passed at `2026-06-12T03:00:28Z` with legacy warnings only |
| Source precommit update/archive check | `python .\tools\check_precommit_update_archive.py --root . --json` | passed at `2026-06-12T03:00:28Z`; changed paths limited to the plan pair |
| Source OpenSpec guard | `python .\tools\run_openspec_guard.py --root .` | passed at `2026-06-12T03:01:39Z` with existing legacy warnings only |
| Source local gate | `.\tools\ci\local_gate.ps1` via `tools/complete_local_flow_to_remote_gate.py --execute --local-gate-step-timeout-seconds 1800` | passed for feature and post-merge local `main` during `b67b94f` integration |
| Source local MR review | `.\tools\ci\local_mr_review.ps1 -Root . -BaseRef main -HeadRef close-general-templates-evidence-20260612 -Json` | passed before `b67b94f` local integration |
| Source local main integration and cleanup | `python .\tools\complete_local_flow_to_remote_gate.py --execute --local-gate-step-timeout-seconds 1800`; `tools/cleanup_integrated_worktree.py` | `main` integrated at `b67b94ff5abfadb13a93d31d0bb7c2b5512a7d97`; rollback ref `refs/backup/local-main/20260612-113345-before-close-general-templates-evidence-20260612`; feature worktree removed; branch deleted; completed claim preserved |
| Source 2026-06-15 plan refresh commit | `git log -1 --oneline` after Task 5 local integration | `ffdfe79 source plan refresh` |
| Source 2026-06-15 remote-base check | `git fetch gitlab`; `git rev-list --left-right --count main...gitlab/main` | `97 0` before final source closeout |
| Source docs registry YAML parse | UTF-8 YAML parse of `docs_bilingual/docs_registry.yaml` | `yaml_ok True`, `documents=109` |
| General 2026-06-15 validation | `powershell -NoProfile -ExecutionPolicy Bypass -File D:\PythonProject_General\tools\ci\local_gate.ps1 -Root D:\PythonProject_General -Json` | passed at `2026-06-15T13:53:42Z`; current `main` is `d2d5a27`; key template files present; `.omx/state` absent; includes hydration, OpenSpec policy, Comet policy, R6 receipt checker, and reusable workflow policy |
| General 2026-06-15 local MR review | `powershell -NoProfile -ExecutionPolicy Bypass -File D:\PythonProject_General\tools\ci\local_mr_review.ps1 -Root D:\PythonProject_General -BaseRef refs/backup/local-main/20260615-before-general-safe-increment -HeadRef main -Json` | passed at `2026-06-15T13:59:29Z`; base ref `refs/backup/local-main/20260615-before-general-safe-increment`; head ref `main`; merge_base `4a7d85890cf10f7d22d88836fc3ee8f5edbd2eb1` |
| General 2026-06-15 final commit | `git -C D:\PythonProject_General log -1 --oneline` | `d2d5a27 general reusable document tools update` |
| General 2026-06-15 rollback ref | `git -C D:\PythonProject_General rev-parse refs/backup/local-main/20260615-before-general-safe-increment` | `4a7d85890cf10f7d22d88836fc3ee8f5edbd2eb1` |
| General_2 2026-06-15 validation | `powershell -NoProfile -ExecutionPolicy Bypass -File D:\PythonProject_General_2\tools\ci\local_gate.ps1 -Root D:\PythonProject_General_2 -Json` | passed at `2026-06-15T13:53:37Z`; current `main` is `101025b`; clean git; root remote CI absent; inert samples present; `.omx/state` absent; includes template health, ownership, subagent-only, OpenSpec, bilingual, name-clarity, local-only, Comet policy, and reusable workflow policy |
| General_2 2026-06-15 local MR review | `powershell -NoProfile -ExecutionPolicy Bypass -File D:\PythonProject_General_2\tools\ci\local_mr_review.ps1 -Root D:\PythonProject_General_2 -BaseRef refs/backup/local-main/20260615-before-general2-safe-increment -HeadRef main -Json` | passed at `2026-06-15T13:59:30Z`; base ref `refs/backup/local-main/20260615-before-general2-safe-increment`; head ref `main`; merge_base `1952f6dda40c9e52c8ced4325aee1ffc407eea67` |
| General_2 2026-06-15 final commit | `git -C D:\PythonProject_General_2 log -1 --oneline` | `101025b general2 local reusable workflow update` |
| General_2 2026-06-15 rollback ref | `git -C D:\PythonProject_General_2 rev-parse refs/backup/local-main/20260615-before-general2-safe-increment` | `1952f6dda40c9e52c8ced4325aee1ffc407eea67` |
| Source 2026-06-15 evidence closeout | final source validation and local-main integration | ready; `check_implementation_plan_rules`、`check_precommit_update_archive`、`run_openspec_guard`、`check_worktree_task_receipt` 已在本工作树通过；local MR review 仍待执行 |
| Remote publication | explicit later user approval required | not_requested; source `main` intentionally leads `gitlab/main` and `github/main` until explicit remote publication |
<!-- EVIDENCE_INDEX_END -->

## Validation Commands

Use the same validation command blocks as the English canonical plan.

## Rollback And Exclusion Rules

- Preserve existing dirty template changes in backup branches before broad rewrites.
- Exclude `.idea/`, caches, build artifacts, local reports, temporary smoke outputs, and non-template-safe runtime receipts.
- Do not run destructive cleanup against computed paths unless resolved absolute paths are inside the intended target repository.
- Do not mutate remote refs without a fresh explicit remote-publication request.
