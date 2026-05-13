# Tasks

## 1. Implementation

- [ ] 1.1 Extend `tools/check_orchestration_trace_evidence.py` with durable workflow and persistent-team threshold evidence validation.
- [ ] 1.2 Add regression tests for `not_needed`, `blocked`, `selected`, and `running` threshold evidence requirements.
- [ ] 1.3 Update orchestration activation governance docs.
- [ ] 1.4 Update stable OpenSpec activation-policy requirement text.
- [ ] 1.5 Keep the slice read-only with no durable-team launch, `.omx/state/` mutation, or user-level state mutation.

## 2. Validation

- [ ] 2.1 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe test\check_orchestration_trace_evidence.test.py`.
- [ ] 2.2 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\check_orchestration_activation_policy.py --root . --json`.
- [ ] 2.3 Run `openspec validate enforce-durable-team-threshold-traces --json`.
- [ ] 2.4 Run `openspec validate --all --json`.
- [ ] 2.5 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\run_openspec_guard.py --root . --tool codex --json`.
- [ ] 2.6 Run local CI gate and local MR review before any local main integration.
