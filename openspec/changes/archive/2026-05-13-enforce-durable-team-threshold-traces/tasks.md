# Tasks

## 1. Implementation

- [x] 1.1 Extend `tools/check_orchestration_trace_evidence.py` with durable workflow and persistent-team threshold evidence validation.
- [x] 1.2 Add regression tests for `not_needed`, `blocked`, `selected`, and `running` threshold evidence requirements.
- [x] 1.3 Update orchestration activation governance docs.
- [x] 1.4 Update stable OpenSpec activation-policy requirement text.
- [x] 1.5 Keep the slice read-only with no durable-team launch, `.omx/state/` mutation, or user-level state mutation.

## 2. Validation

- [x] 2.1 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe test\check_orchestration_trace_evidence.test.py`. Evidence: 13 tests OK.
- [x] 2.2 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\check_orchestration_activation_policy.py --root . --json`. Evidence: `ok=true`; only repo-local LangGraph backend context missing warning from capability-chain subcheck.
- [x] 2.3 Run `openspec validate enforce-durable-team-threshold-traces --json`. Evidence: passed after removing UTF-8 BOM from the delta spec so OpenSpec parsed 2 MODIFIED deltas.
- [x] 2.4 Run `openspec validate --all --json`. Evidence before archive: 76/76 passed; after archive: 75/75 stable specs passed.
- [x] 2.5 Run `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\run_openspec_guard.py --root . --tool codex --json`. Evidence: 19/19 guard steps passed after adding this worktree session claim and closing the stale claim for the already merged `enforce-capability-switch-chain` worktree.
- [x] 2.6 Run local CI gate before archive. Evidence: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -Json -StepTimeoutSeconds 180` passed 5/5 steps after the session-claim fix. Local MR review is rerun after the archive commit so it can verify the final clean branch state.
