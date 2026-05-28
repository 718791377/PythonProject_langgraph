# Change: Harden Project MOE Phase 1 CLI Envelope Schema

## Why

The Project MOE GUI plan requires Phase 1 readiness checks to fail closed when a target project's read-only Mode CLI reports an unsupported JSON envelope schema. The current common envelope validator checks required fields, command echo, ok/token, CLI contract, and private-field exposure, but it does not explicitly reject a present `schema_version` value that differs from this toolchain's supported `SCHEMA_VERSION`.

## What Changes

- Add a stable fail-closed blocker for Mode CLI envelope `schema_version` mismatches.
- Cover the mismatch through the Phase 1 readiness checker read-contract path.
- Keep static-only and static-blocker behavior unchanged: static-only never executes the target CLI, and read-contract execution remains limited to safe read commands.
- Update the Project MOE GUI implementation-plan checklist only for evidence that is actually covered by existing and new tests.

## Impact Scope

- `tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py` - shared Project MOE GUI toolchain validator source
- `test/project_moe_gui_toolchain.test.py` - Project MOE GUI toolchain regression test suite
- `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md` - Chinese implementation plan and evidence checklist
- this OpenSpec change package

## Explicit Non-Goals

- No real target-project writes.
- No GUI control-mode rollout to `D:\PythonProject_paper_suggest` or any other consumer project.
- No remote GitLab or GitHub publication.
- No change to the target Mode CLI write-command contract.

## Rollout Sequence

1. Add the OpenSpec change and management checklist.
2. Add the schema-version mismatch blocker and remediation metadata.
3. Add targeted tests for unsupported read-contract envelope schema.
4. Update the implementation-plan evidence checklist for the covered Phase 1 readiness items.
5. Run targeted tests, OpenSpec validation, precommit update/archive review, local gate, and local MR review.
6. Merge the clean feature branch into local `main` only after local validation passes.

## Rollback Plan

- Revert the feature branch or the local main merge commit.
- If local main has already advanced, use the rollback ref created before merge.
- No target project state is written by this slice, so no external rollback is required.

## Validation Path

- `python test\project_moe_gui_toolchain.test.py` - run the Project MOE GUI toolchain regression suite
- `openspec validate harden-project-moe-cli-envelope-schema-20260528 --strict` - validate this bounded OpenSpec change package
- `python .\tools\check_precommit_update_archive.py --root . --json` - run the required update/archive review before commit
- `python .\tools\run_openspec_guard.py --root .` - run repository OpenSpec and governance guards
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - run the shared local CI gate
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - run local MR review before local main integration

## Mainline Classification

- Owning mainline: Project MOE GUI toolchain implementation under the Codex user-level orchestration repository.
- Related mainline: user-level orchestration control-surface safety and local-first publication governance.
