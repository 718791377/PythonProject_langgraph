# Change: Harden Project MOE Phase 1 Readiness Output Contract

## Why

The Project MOE GUI plan still has one open Phase 1 readiness-schema item: the readiness checker output must explicitly expose the adaptation lane, blockers, warnings, checked files, redacted paths, and `control_mode_allowed`. Some of those values already exist, but the machine-readable contract does not yet have explicit `warnings`, `checked_files`, and `redacted_paths` fields.

## What Changes

- Add explicit `warnings`, `checked_files`, and `redacted_paths` fields to the Phase 1 readiness JSON payload.
- Keep existing lane, blocker, and control-mode fields stable.
- Add regression coverage for the output contract on a Ready Lane target.
- Update the Project MOE GUI implementation-plan checklist only after test evidence exists.

## Scope

- `tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py` - implements the additive readiness evidence fields.
- `test/project_moe_gui_toolchain.test.py` - covers ready and static-only readiness output contracts.
- `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md` - records the English implementation-plan checklist evidence.
- `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md` - records the Chinese implementation-plan checklist evidence.
- This OpenSpec change package.

## Non-Goals

- Do not write any real target project.
- Do not enable GUI control for `D:\PythonProject_paper_suggest` or any other target project.
- Do not change target Mode CLI write commands.
- Do not push GitLab/GitHub.

## Rollout

1. Create this OpenSpec package and local governance record.
2. Add the readiness output contract fields.
3. Add targeted regression assertions.
4. Update the implementation-plan checklist based on evidence.
5. Run targeted tests, OpenSpec validation, repository guard, local gate, and local MR review.
6. Merge to local `main` after local evidence passes.

## Rollback

- Revert the feature branch or the local `main` merge commit.
- If local `main` has moved, use the rollback ref created before integration.
- No external target project state is changed by this slice.

## Verification

- `python test\project_moe_gui_toolchain.test.py` - runs the targeted Project MOE GUI toolchain regression suite.
- `openspec validate harden-moe-readiness-output-contract-20260528 --strict` - validates the active OpenSpec delta.
- `python .\tools\check_precommit_update_archive.py --root . --json` - enforces the pre-commit update/archive review.
- `python .\tools\run_openspec_guard.py --root .` - runs the repository OpenSpec guard.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs the local MR review gate.
