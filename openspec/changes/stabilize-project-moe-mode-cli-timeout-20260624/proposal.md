# Change: Stabilize Project MOE Mode CLI Timeout Budget

## Why

Full repository gates intermittently reported `blocked:mode_cli_timeout` in Project MOE GUI tests while focused reruns passed. The root cause is that the GUI toolchain used a hard-coded 20 second Mode CLI subprocess timeout, which is too tight on loaded Windows hosts during full-suite execution.

## What Changes

- Replace the hard-coded Mode CLI timeout with a shared 60 second default budget.
- Allow operators and tests to override the budget through `PROJECT_MOE_GUI_MODE_CLI_TIMEOUT_SECONDS`.
- Apply the same budget path to the shared toolchain read-contract runner and the GUI shell write/readback runner.
- Add regression tests that prove explicit env override, default full-suite headroom, and write/readback consistency.
- Keep timeout handling fail-closed: invalid, zero, or negative override values fall back to the bounded default.

## Capabilities

### New Capabilities
- `project-moe-mode-cli-timeout-budget`: Defines the configurable Mode CLI timeout budget for Project MOE GUI read and write subprocess calls.

### Modified Capabilities
- None.

## Impact

- `tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py`: shared Mode CLI read-contract runner timeout helper.
- `tools/project_moe_gui_toolchain/src/project_moe_gui/gui_shell.py`: GUI shell Mode CLI write/readback timeout helper.
- `test/project_moe_gui_toolchain.test.py`: focused timeout-budget regression coverage.
- `openspec/changes/stabilize-project-moe-mode-cli-timeout-20260624`: local stabilization change package.

## Impact Scope

Owning mainline: Project MOE GUI toolchain stabilization inside the Codex user-level orchestration repository.
Related mainline: Codex npm EPERM rollout closeout, because this hotfix unblocks its local gate validation.

## Explicit Non-Goals

- Do not change Mode CLI command semantics or JSON envelope shape.
- Do not make the GUI wait without a bounded timeout.
- Do not suppress real timeout failures after the configured budget expires.
- Do not mutate target project state beyond existing write actions.
- Do not perform any remote publication.

## Rollout Sequence

1. Record this bounded OpenSpec/Comet package.
2. Add tests proving configurable timeout behavior and full-suite headroom.
3. Add the shared timeout helper in both toolchain and GUI shell surfaces.
4. Run focused Project MOE timeout tests and the full Project MOE toolchain test file.
5. Run OpenSpec validation, precommit update/archive review, repository guard, local gate, and local MR review.
6. Merge into local `main` through the guarded local-main helper and stop before remote publication.

## Rollback Plan

Revert the hotfix commit or use the rollback ref created by the local-main integration helper. No external target project state is changed by this slice.

## Validation Path

- `python test\project_moe_gui_toolchain.test.py -k timeout -v`: focused timeout-budget regression tests.
- `python test\project_moe_gui_toolchain.test.py -v`: full Project MOE GUI toolchain regression file.
- `openspec validate stabilize-project-moe-mode-cli-timeout-20260624 --strict`: validate this change package.
- `python .\tools\check_precommit_update_archive.py --root . --json`: precommit update/archive review.
- `python .\tools\run_openspec_guard.py --root . --tool codex --json`: repository OpenSpec/governance guard.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 3600`: shared local CI gate with full-suite headroom.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1`: local MR review before local main integration.

## Mainline Classification

This is a bounded subproblem of the Project MOE GUI toolchain mainline and a stabilization dependency for the current Codex npm EPERM rollout. It is not a new long-term mainline.
