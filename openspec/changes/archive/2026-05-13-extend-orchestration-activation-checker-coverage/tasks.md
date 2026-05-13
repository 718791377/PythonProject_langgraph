# Tasks

- [x] Update activation policy and stable spec wording for advanced routing enforcement coverage.
- [x] Extend `tools/check_orchestration_activation_policy.py` required snippets.
- [x] Add checker regression tests for missing advanced coverage.
- [x] Defer `tools/ci/ci_test_manifest.json` registration because another active claim owns that path.
- [x] Validate with targeted tests, OpenSpec guard, and local gate.

## Validation Evidence

- `python tools/check_orchestration_activation_policy.py --root . --json` - passed.
- `python test/check_orchestration_activation_policy.test.py` - passed, 6 tests.
- `openspec validate extend-orchestration-activation-checker-coverage --json` - passed.
- `openspec validate --all --json` - passed, 76 items.
- `python tools/run_openspec_guard.py --root . --tool codex --json` - passed, 18/18 steps.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -Json -StepTimeoutSeconds 180` - passed, 5/5 steps.

