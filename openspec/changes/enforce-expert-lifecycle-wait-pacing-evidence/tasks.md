# Tasks

## 1. Implementation

- [ ] 1.1 Add `tools/check_expert_lifecycle_wait_pacing_evidence.py`.
- [ ] 1.2 Add regression tests for completed expert closure, preserved-thread exceptions, bounded waits, indefinite waits, stall actions, and provider backpressure labels.
- [ ] 1.3 Update orchestration activation governance docs.
- [ ] 1.4 Update stable OpenSpec activation-policy requirement text.
- [ ] 1.5 Extend `tools/check_orchestration_activation_policy.py` so policy surfaces mention and load the new checker.
- [ ] 1.6 Keep the slice read-only with no durable-team launch, `.omx/state/` mutation, user-level state mutation, or CI manifest edit.

## 2. Validation

- [ ] 2.1 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe test\check_expert_lifecycle_wait_pacing_evidence.test.py`.
- [ ] 2.2 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe test\check_orchestration_activation_policy.test.py`.
- [ ] 2.3 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\check_orchestration_activation_policy.py --root . --json`.
- [ ] 2.4 Run `openspec validate enforce-expert-lifecycle-wait-pacing-evidence --json`.
- [ ] 2.5 Run `openspec validate --all --json`.
- [ ] 2.6 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\run_openspec_guard.py --root . --tool codex --json`.
- [ ] 2.7 Run local CI gate.
- [ ] 2.8 Run local MR review after the branch is clean.
