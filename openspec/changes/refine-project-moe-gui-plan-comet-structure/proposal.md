## Why

`project_moe_agent_gui_toolchain_plan.zh-CN.md` was already refactored once, but it still needs a full `/comet` package with Open / Design / Build / Verify evidence, archive deferral, ordered tasks, and readiness-lane explanation. This refactor prevents later implementation work from confusing "plan structure is done" with "target project GUI runtime is done."

## What Changes

- Refactor `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md` so it matches the newer Pi sidecar plan family: goal, architecture, source of truth, contract, gate, rollback, risk, self-check, and verification order.
- Add a complete Comet/OpenSpec active-change package: proposal, design, delta spec, tasks, management, and `.comet.yaml`.
- Add Superpowers design and implementation-plan records so this refactor has durable design and execution notes.
- Clearly state that `D:\PythonProject_paper_suggest` remains blocked/repair-lane evidence and must not be mislabeled ready.
- Record archive deferral explicitly: after feature-branch submission, archive waits for the later local integration and verification decision.

## Capabilities

### New Capability

- `project-moe-agent-gui-plan-contract`: constrains the Project MOE GUI implementation plan to a clear documentation structure, readiness metadata, GUI runtime completion boundary, and remote-publication boundary.

### Modified Capability

- None. This change adds document-contract context only and does not modify an existing stable capability.

## Impact

- Affected docs: `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md`
- Affected OpenSpec artifacts: `openspec/changes/refine-project-moe-gui-plan-comet-structure/`
- Affected Superpowers artifacts: `docs/superpowers/specs/2026-05-27-project-moe-gui-plan-comet-design.md` and `docs/superpowers/plans/2026-05-27-refine-project-moe-gui-plan-comet-structure.md`
- No runtime code, dependency install, target-project write, GitLab/GitHub publication, or PySide6 installation is performed by this change.

## Governance Fields

- `impact_scope`: documentation plan plus active OpenSpec artifacts only.
- `explicit_non_goals`: runtime implementation, target project writes, PySide6 install, remote publication, user-level config mutation.
- `rollout_sequence`: feature worktree -> document rewrite -> local validation -> feature branch commit -> local main integration decision.
- `rollback_plan`: revert the feature branch commit or reset the local branch to the pre-change base.
- `validation_path`: `git diff --check`, `openspec validate`, implementation-plan checker, precommit update/archive gate, OpenSpec guard, local MR review.
- `mainline_classification`: Project MOE GUI documentation and implementation-planning lane in the repository's user-level orchestration product line.
