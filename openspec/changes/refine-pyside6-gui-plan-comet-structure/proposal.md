## Why

`pyside6_cross_project_gui_capability_plan.*` already captured the shared PySide6 runtime strategy, but its structure predated the newer executable Comet plan family. It needed the same clear boundaries used by the Pi sidecar and Comet runtime plans: status interpretation, relationship model, explicit gates, source-of-truth map, JSON contracts, implementation checklist, local integration order, and honest verification evidence.

## What Changes

- Refactor the bilingual PySide6 cross-project GUI capability plan into the full Comet executable-plan structure.
- Preserve the shared runtime default path, local-only runtime rule, consumer-project ownership model, and explicit-trigger gates for override, visible GUI, and packaging.
- Add a Comet/OpenSpec support package and Superpowers design/implementation records for this documentation refactor.
- Record that the current change performs no PySide6 install, no consumer-project write, no visible GUI launch, no packaging, and no remote publication.

## Capabilities

### New Capability

- `pyside6-cross-project-gui-plan-contract`: constrains the PySide6 cross-project GUI plan to separate shared-runtime readiness, consumer-project GUI readiness, explicit high-impact trigger gates, and local-main-first publication boundaries.

### Modified Capability

- None. This change adds a plan-contract active change and rewrites the implementation-plan pair.

## Impact

- Affected docs: `docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md` and `.zh-CN.md`.
- Affected OpenSpec artifacts: `openspec/changes/refine-pyside6-gui-plan-comet-structure/`.
- Affected Superpowers artifacts: `docs/superpowers/specs/2026-05-27-pyside6-gui-plan-comet-design.md` and `docs/superpowers/plans/2026-05-27-refine-pyside6-gui-plan-comet-structure.md`.
- No runtime code, dependency install, target-project write, visible GUI launch, executable packaging, GitLab/GitHub publication, or user-level config mutation is performed.

## Governance Fields

- `impact_scope`: documentation plan plus active OpenSpec/Superpowers artifacts.
- `explicit_non_goals`: PySide6 install, target-project writes, visible GUI, packaging, user-level config mutation, remote publication.
- `rollout_sequence`: feature worktree -> document rewrite -> local validation -> feature branch commit -> local CI/MR review -> local main integration.
- `rollback_plan`: revert the feature branch commit or reset local `main` to the pre-merge backup ref.
- `validation_path`: `git diff --check`, `openspec validate`, implementation-plan checker, precommit update/archive gate, OpenSpec guard, local gate, local MR review.
