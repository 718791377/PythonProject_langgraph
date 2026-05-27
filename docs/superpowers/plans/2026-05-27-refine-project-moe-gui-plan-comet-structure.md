---
change: refine-project-moe-gui-plan-comet-structure
design-doc: docs/superpowers/specs/2026-05-27-project-moe-gui-plan-comet-design.md
base-ref: 9fbc66e
---

# Refine Project MOE GUI Plan Comet Structure Implementation Plan

> **For agentic workers:** Use the `$comet` control layer and `superpowers:executing-plans` style execution for the plan refactor and bounded guarded-uninstall continuation. Track every item with checkbox syntax. Do not claim unrun Comet bash scripts passed.

**Goal:** Rewrite the Project MOE Agent GUI implementation plan into a complete `/comet`-traceable executable-plan structure aligned with the newer Pi sidecar plan and Comet runtime agile focus-area plan.

**Scope:** Complete the implementation-plan/OpenSpec/Superpowers refactor and add one bounded toolchain implementation slice for guarded uninstall `--apply`, with tests and operations documentation. Do not install PySide6, roll out to real target projects, edit user-level directories, or publish remote refs.

---

## Step 1: Confirm the existing Comet / OpenSpec change

- [x] Reuse `openspec/changes/refine-project-moe-gui-plan-comet-structure/`.
- [x] Confirm `.comet.yaml` is in `phase: verify` and records `comet_script_state: blocked:bash_not_found_on_windows`.
- [x] Confirm the initial pass was plan structure and evidence closure; record this continuation as a bounded runtime slice rather than mislabelling it documentation-only.

## Step 2: Refactor the target plan structure

- [x] Update the English source `project_moe_agent_gui_toolchain_plan.md` to the full Comet structure.
- [x] Update the Chinese paired file `project_moe_agent_gui_toolchain_plan.zh-CN.md`.
- [x] Preserve `status: draft` and use `plan_readiness` for implementation-slicing readiness.
- [x] Align with the Pi sidecar plan structure: review conclusion, relationship model, goals/non-goals, runtime architecture, source of truth, install artifacts, CLI/JSON/state contracts, readiness gates, rollback, risks, and self-check.
- [x] Align with Comet runtime semantics: management record, phase gates, Monitoring return, implementation slices, file ownership map, local integration order, and evidence retention.

## Step 3: Repair support artifacts

- [x] Repair mojibake/question-mark placeholders in `tasks.zh-CN.md`.
- [x] Repair mojibake/question-mark placeholders in `design.zh-CN.md`.
- [x] Repair the Chinese Superpowers design document.
- [x] Repair the Chinese Superpowers implementation plan.
- [x] Repair the Chinese management record.

## Step 4: Verify

- [x] Run `git diff --check`.
- [x] Run `openspec validate refine-project-moe-gui-plan-comet-structure --strict`.
- [x] Run `python .\tools\check_implementation_plan_rules.py --root . --json`.
- [x] Run `python .\tools\check_precommit_update_archive.py --root . --json`.
- [x] Run `python .\tools\run_openspec_guard.py --root .`.

## Step 5: Commit and integrate locally

- [x] Commit the feature branch with Chinese commit messages.
- [x] Run `.\tools\ci\local_gate.ps1` after commit.
- [x] Run `.\tools\ci\local_mr_review.ps1` after commit.
- [ ] Merge into local `main` under the user-approved local integration flow.
- [ ] Confirm the primary worktree HEAD equals local `main`.

## Step 6: Guarded uninstall apply continuation

- [x] Implement `plan_project_moe_gui_uninstall.py --apply` for fixed-allowlist, manifest-hash-verified managed file deletion only.
- [x] Preserve `MOE.md`, `.codex/agents/*.toml`, and `.omx/state`; fail closed on unsafe manifest entries before deletion.
- [x] Update targeted tests, the operations guide, the plan pair, and OpenSpec contract artifacts.
- [x] Re-run toolchain tests, repository guards, local gate, and local MR review before local `main` integration.

## Non-goals

- [ ] Do not push GitLab / GitHub.
- [ ] Do not open or merge remote MRs.
- [ ] Do not write to `D:\PythonProject_paper_suggest`.
- [ ] Do not mark `D:\PythonProject_paper_suggest` as GUI ready.
