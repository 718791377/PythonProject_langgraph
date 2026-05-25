## Why

The Project MOE Agent GUI toolchain plan has accumulated new local facts after the launcher readiness-gate work. The plan needs a Comet-tracked documentation refresh so future cold-start sessions can distinguish implemented repository fixtures from real target-project readiness and avoid unsafe duplicate worktrees or unauthorized remote publication.

## What Changes

- Refresh the Chinese Project MOE Agent GUI toolchain implementation plan with current Comet/cold-start continuation boundaries.
- Clarify that `status: draft` remains correct until real target-project readiness and GUI control evidence exist.
- Preserve target-project safety boundaries: readiness first, no direct state writes, no remote publication without explicit approval.
- Record the Comet tracking limitation in this Windows session: Comet shell scripts require `bash`, which is not available in the current shell, so OpenSpec artifacts and repository gates are the traceable fallback.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None.

## Impact

- Affected document:
  - `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md` - Chinese implementation plan documenting Project MOE Agent GUI toolchain status and gates
- Affected workflow artifact:
  - `openspec/changes/refresh-project-moe-gui-plan-comet/` - Comet/OpenSpec trace directory for this documentation tweak
- No runtime code, target-project files, user-level Codex home files, or remote refs are changed by this documentation refresh.

## impact_scope

- single implementation-plan document refresh
- Comet/OpenSpec traceability for a small documentation tweak
- no target-project mutation and no remote publication

## explicit_non_goals

- no real GUI installation or control in `D:\PythonProject_paper_suggest`
- no change to PySide6 runtime provisioning
- no new Project MOE GUI runtime capability
- no modification of target-project `.omx/state`, `MOE.md`, Agent TOML, or wrappers
- no GitLab/GitHub publication

## rollout_sequence

1. Reuse the existing `project-moe-agent-gui-toolchain-plan` feature worktree because ownership precheck found an active claim for the target file.
2. Rebase the worktree onto current local `main` to avoid reverting already integrated work.
3. Create lightweight Comet/OpenSpec artifacts for this documentation tweak.
4. Update the Chinese implementation plan with current cold-start, Comet, and readiness-boundary facts.
5. Run document/update/archive checks and local review gates.
6. Commit locally on the feature branch and stop before local-main integration or remote publication unless explicitly authorized.

## rollback_plan

- Revert the single feature-branch commit that updates the plan and Comet artifact if the wording proves misleading.
- Remove or archive the `refresh-project-moe-gui-plan-comet` change artifacts if the repository chooses not to retain this Comet trace.
- Do not touch target projects or user-level runtime assets during rollback.

## validation_path

- `git diff --check` - checks whitespace and patch formatting before commit
- `python .\tools\check_precommit_update_archive.py --root . --json` - enforces pre-commit update/archive readiness
- `python .\tools\run_openspec_guard.py --root .` - runs the repository OpenSpec and governance guard suite
- `.\tools\ci\local_mr_review.ps1` - performs local MR-style review after the feature commit

## mainline_classification

- existing mainline: Project MOE Agent GUI toolchain documentation and cross-project GUI governance
