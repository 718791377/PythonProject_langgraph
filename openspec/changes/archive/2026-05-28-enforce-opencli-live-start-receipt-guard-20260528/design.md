# Design: OpenCLI live-start evidence guard

## Approach

Add a repo-local `start` preflight to `tools/opencli_governance.py`. It reuses the existing owner-registry lookup and port-lease validation, then validates a generic OpenCLI install/update receipt with the same field family used by user-level update receipts.

## Safety model

- The command is governance-only and never starts OpenCLI.
- It never launches a browser, connects to a browser target, reads cookies, executes JavaScript, clicks, types, navigates, or mutates user-level Codex configuration.
- Missing evidence returns exit code `3` and `opencli_live_start_blocked`.
- Complete evidence returns exit code `4` and `live_start_not_implemented_repo_local_mvp`, proving that repo-local MVP still defers real live-start.
- Output hashes private install, wrapper, state, and rollback paths.

## Receipt validation

The install receipt requires tool name, installed version, source URL, install path, wrapper path, state path, smoke test command, passing smoke result, updater command, rollback pointer, owner lane, and redaction status. Sensitive keys or inline secrets fail closed.

## Acceptance evidence

- `python test\cdp_bridge_governance.test.py` - targeted unit coverage for CDP Bridge, OpenCLI, and CLI-Anything governance fixtures.
- `python tools/run_openspec_guard.py --root . --json` - repository OpenSpec and governance guard.
- `powershell -NoProfile -File tools/ci/local_gate.ps1 -Json` - shared local CI gate.
- `powershell -NoProfile -File tools/ci/local_mr_review.ps1 -Json` - local MR review and merge simulation gate.
