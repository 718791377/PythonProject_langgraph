---
change: refine-pyside6-gui-plan-comet-structure
design-doc: docs/superpowers/specs/2026-05-27-pyside6-gui-plan-comet-design.md
base-ref: 8a4aee5
---

# Refine PySide6 GUI Plan Comet Structure Implementation Plan

> **For agentic workers:** Use `$comet` and `superpowers:executing-plans` style execution. This is a documentation/governance refactor only. Do not install PySide6, write consumer projects, launch visible GUI windows, package executables, or push remote refs.

**Goal:** Rewrite the PySide6 cross-project GUI capability implementation plan into a full `/comet`-traceable executable-plan structure aligned with the Pi sidecar and Comet runtime plan family.

## Step 1: Confirm change scope

- [x] Use a dedicated feature worktree.
- [x] Create OpenSpec change `refine-pyside6-gui-plan-comet-structure`.
- [x] Record `.comet.yaml` with `comet_script_state: blocked:bash_not_found_on_windows`.
- [x] Confirm the change is documentation/OpenSpec only.

## Step 2: Refactor target plans

- [x] Update the English source plan.
- [x] Update the Chinese companion plan.
- [x] Preserve PySide6-specific facts and explicit trigger gates.
- [x] Align structure with the Pi sidecar and Comet runtime plans.

## Step 3: Verify

- [ ] Run `git diff --check`.
- [ ] Run `openspec validate refine-pyside6-gui-plan-comet-structure --strict`.
- [ ] Run `python .\tools\check_implementation_plan_rules.py --root . --json`.
- [ ] Run `python .\tools\check_precommit_update_archive.py --root . --json`.
- [ ] Run `python .\tools\run_openspec_guard.py --root .`.

## Step 4: Commit and integrate locally

- [x] Commit with a Chinese message.
- [x] Run local gate.
- [x] Run local MR review.
- [ ] Create a local-main rollback backup ref.
- [ ] Fast-forward merge into local `main`.
- [ ] Preserve completed receipt/claim and clean the integrated worktree.

## Non-goals

- [ ] Do not push GitLab/GitHub.
- [ ] Do not open or merge remote MRs.
- [ ] Do not install PySide6.
- [ ] Do not write consumer projects.
- [ ] Do not launch visible GUI or package executables.
