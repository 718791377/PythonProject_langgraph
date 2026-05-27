## 1. Open / Design Artifacts

- [x] 1.1 Create full Comet/OpenSpec change `refine-pyside6-gui-plan-comet-structure`.
- [x] 1.2 Record proposal, design, management checklist, `.openspec.yaml`, and `.comet.yaml`.
- [x] 1.3 Record Windows bash unavailability as a Comet script-state blocker instead of fabricating transitions.
- [x] 1.4 Create delta spec `pyside6-cross-project-gui-plan-contract`.

## 2. Superpowers Artifacts

- [x] 2.1 Create design doc `docs/superpowers/specs/2026-05-27-pyside6-gui-plan-comet-design.md`.
- [x] 2.2 Create implementation plan `docs/superpowers/plans/2026-05-27-refine-pyside6-gui-plan-comet-structure.md`.

## 3. Document Refactor

- [x] 3.1 Rewrite the English and Chinese PySide6 plan pair into the full Comet executable-plan structure.
- [x] 3.2 Preserve PySide6-specific facts: shared runtime path, local-only runtime, consumer ownership, per-project wrapper default, and explicit-trigger gates.
- [x] 3.3 Align with Pi sidecar plan structure: review conclusion, relationship model, goals/non-goals, runtime architecture, source of truth, contracts, gates, rollback, risks and self-check.
- [x] 3.4 Align with Comet runtime semantics: management record, phase gates, Monitoring return semantics, implementation slices, file ownership map, local integration order and evidence retention.

## 4. Verification

- [x] 4.1 Run `git diff --check`.
- [x] 4.2 Run `openspec validate refine-pyside6-gui-plan-comet-structure --strict`.
- [x] 4.3 Run `python .\tools\check_implementation_plan_rules.py --root . --json`.
- [x] 4.4 Run `python .\tools\check_precommit_update_archive.py --root . --json`.
- [x] 4.5 Run `python .\tools\run_openspec_guard.py --root .`.
- [x] 4.6 Run local gate and local MR review after commit.
