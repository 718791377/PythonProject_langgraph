# Tasks

## 1. Implementation

- [x] 1.1 Add `tools/check_expert_lifecycle_wait_pacing_evidence.py`.
- [x] 1.2 Add regression tests for completed expert closure, preserved-thread exceptions, bounded waits, indefinite waits, stall actions, and provider backpressure labels.
- [x] 1.3 Update orchestration activation governance docs.
- [x] 1.4 Update stable OpenSpec activation-policy requirement text.
- [x] 1.5 Extend `tools/check_orchestration_activation_policy.py` so policy surfaces mention and load the new checker.
- [x] 1.6 Keep the slice read-only with no durable-team launch, `.omx/state/` mutation, user-level state mutation, or CI manifest edit.

## 2. Validation

- [x] 2.1 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe test\check_expert_lifecycle_wait_pacing_evidence.test.py`.
- [x] 2.2 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe test\check_orchestration_activation_policy.test.py`.
- [x] 2.3 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\check_orchestration_activation_policy.py --root . --json`.
- [x] 2.4 Run `openspec validate enforce-expert-lifecycle-wait-pacing-evidence --json`.
- [x] 2.5 Run `openspec validate --all --json`.
- [x] 2.6 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\run_openspec_guard.py --root . --tool codex --json`.
- [x] 2.7 Run local CI gate.
- [x] 2.8 Run local MR review after the branch is clean.

## 3. Evidence

- `test\check_expert_lifecycle_wait_pacing_evidence.test.py`: 11 tests passed.
- `test\check_orchestration_activation_policy.test.py`: 12 tests passed.
- `tools\check_orchestration_activation_policy.py --root . --json`: passed with `ok=true`; repo-local LangGraph backend context warning is non-blocking for this checker slice.
- `openspec validate enforce-expert-lifecycle-wait-pacing-evidence --json`: passed before archive.
- `openspec validate --all --json`: passed before archive and after archive.
- `tools\run_openspec_guard.py --root . --tool codex --json`: passed.
- `git diff --check`: passed.
- `tools\ci\local_gate.ps1 -Root . -Json -StepTimeoutSeconds 180`: passed with `ok=true`, 5/5 steps passed, including 19/19 OpenSpec guard steps, 23 manifest Python tests, empty node/powershell manifests, and `git diff --check`.
- `tools\ci\local_mr_review.ps1 -Root . -Json`: passed with `ok=true`; branch was clean, 2 commits over `main`, 13 changed files, and merge-tree conflict count was 0.
