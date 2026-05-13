# Tasks

## 1. Implementation

- [x] 1.1 Add `tools/check_custom_agent_toml_schema.py`.
- [x] 1.2 Add `test/check_custom_agent_toml_schema.test.py`.
- [x] 1.3 Register the checker in `tools/safety_rule_script_backing_registry.json`.
- [x] 1.4 Wire the checker into `tools/run_openspec_guard.py` JSON and text paths.
- [x] 1.5 Update AGENTS.md and orchestration activation governance docs.
- [x] 1.6 Update stable OpenSpec requirement text.
- [x] 1.7 Defer `tools/ci/ci_test_manifest.json` registration because another active claim owns that path.

## 2. Validation

- [x] 2.1 Run the custom agent TOML schema checker test.
- [x] 2.2 Run the custom agent TOML schema checker against this worktree.
- [x] 2.3 Run `tools/check_orchestration_activation_policy.py`.
- [x] 2.4 Run `tools/run_openspec_guard.py`.
- [x] 2.5 Run `openspec validate --all`.
- [x] 2.6 Run local gate and local MR review before any local main integration.

## Validation Evidence

- `python test/check_custom_agent_toml_schema.test.py` - passed, 6 tests.
- `python test/check_orchestration_activation_policy.test.py` - passed, 7 tests.
- `python tools/check_custom_agent_toml_schema.py --root . --json` - passed; checked 24 user-level agent TOMLs, repo-local agents directory missing warning only.
- `python tools/check_orchestration_activation_policy.py --root . --json` - passed.
- `python tools/check_safety_rule_script_backing.py --root . --json` - passed.
- `openspec validate enforce-custom-agent-toml-schema --json` - passed.
- `openspec validate --all --json` - passed, 76 items.
- `python tools/run_openspec_guard.py --root . --tool codex --json` - passed, 19/19 steps.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -Json -StepTimeoutSeconds 180` - passed, 5/5 steps.
