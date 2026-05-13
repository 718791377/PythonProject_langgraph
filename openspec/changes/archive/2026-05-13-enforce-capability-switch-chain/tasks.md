# Tasks

## 1. Implementation

- [x] 1.1 Add `tools/check_capability_switch_chain.py`.
- [x] 1.2 Add `test/check_capability_switch_chain.test.py`.
- [x] 1.3 Make `tools/check_orchestration_activation_policy.py` invoke the capability-switch checker.
- [x] 1.4 Update `test/check_orchestration_activation_policy.test.py` for the subcheck.
- [x] 1.5 Update AGENTS.md and orchestration activation governance docs.
- [x] 1.6 Update stable OpenSpec requirement text.
- [x] 1.7 Avoid `tools/ci/ci_test_manifest.json`, `tools/run_openspec_guard.py`, and safety registry edits in this slice because existing guard wiring or active ownership makes direct edits unnecessary or unsafe.

## 2. Validation

- [x] 2.1 Run the capability switch chain checker test. Evidence: `D:\PythonProject_langgraph\.venv\Scripts\python.exe test\check_capability_switch_chain.test.py` (9 tests OK).
- [x] 2.2 Run the capability switch chain checker against this worktree. Evidence: `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\check_capability_switch_chain.py --root . --json` (`ok=true`; repo-local backend context missing only as warning).
- [x] 2.3 Run orchestration activation policy tests and checker. Evidence: `test\check_orchestration_activation_policy.test.py` (8 tests OK) and `tools\check_orchestration_activation_policy.py --root . --json` (`ok=true`; capability subcheck warning only).
- [x] 2.4 Run OpenSpec validation. Evidence: `openspec validate enforce-capability-switch-chain --json` passed and `openspec validate --all --json` reported 76/76 passed.
- [x] 2.5 Run OpenSpec guard. Evidence: `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\run_openspec_guard.py --root . --tool codex --json` passed 19/19 guard steps after clarifying validation-path list items.
- [x] 2.6 Run local gate and local MR review before any local main integration. Evidence before archive commit: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -Json -StepTimeoutSeconds 180` passed 5/5 steps, and `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -Root . -Json` passed with a clean worktree, clean merge-tree, and 0 errors. The first local MR review attempt used an unsupported `-StepTimeoutSeconds` argument and was discarded as operator command error, not product validation evidence.
