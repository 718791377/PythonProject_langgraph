## Why

The user-level MCP, skills, browser, and CLI governance plan requires `chrome-devtools-mcp` to move from a bare entry toward a managed browser automation surface. The previous browser owner registry slice created the ownership primitive; this slice adds the repository-local `chrome-devtools-mcp` managed wrapper MVP for isolated sessions without installing a user-level wrapper or starting a real browser.

## What Changes

- Add `tools/chrome_devtools_mcp_managed.py` as a repo-local wrapper contract for `chrome-devtools-mcp` isolated-session mode.
- Support `isolated-session plan`, `reserve`, `start --dry-run`, fail-closed live `start`, `release`, and `status` commands.
- Delegate lease writes and releases to `tools/browser_owner_registry.py`.
- Keep default output sanitized by exposing profile-path and receipt-path hashes instead of raw private paths.
- Keep the repo-local MVP non-invasive: it does not launch Chrome, connect to CDP, mutate user-level Codex config, read cookies, or write human-owned profiles.
- Register focused unit tests in the shared CI test manifest and update bilingual plan state.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-mcp-skills-browser-cli-governance`: add the repo-local `chrome-devtools-mcp` managed wrapper isolated-session MVP and its fail-closed live-start boundary.

## Impact

- Affected source: `tools/chrome_devtools_mcp_managed.py`.
- Affected tests: `test/chrome_devtools_mcp_managed.test.py`, `tools/ci/ci_test_manifest.json`.
- Affected governance docs: bilingual implementation plan and OpenSpec delta/stable spec surfaces.
- No user-level files under `C:\Users\lenovo\.codex` are modified by this slice.
- No Chrome instance is launched and no CDP endpoint is contacted by this slice.

## Mainline classification

Existing mainline: user-level MCP, skills, browser automation, and CLI harness governance.

## Explicit non-goals

- Do not install or replace the user-level `chrome-devtools-mcp` wrapper.
- Do not launch Chrome, connect to CDP, click/type/navigate, read cookies, inspect user-owned browser data, or modify `C:\Users\lenovo\.codex\config.toml`.
- Do not implement project-profile mode, stale cleanup execution, CDP Bridge/OpenCLI enforcement, `oh-my-pi`, CLI-Anything, or `wecom-cli` in this slice.
- Do not delete profile directories; cleanup behavior remains deferred to later safe cleanup dry-run and execution slices.

## Rollout sequence

1. Add OpenSpec artifacts for the `chrome-devtools-mcp` isolated-session wrapper MVP slice.
2. Implement the repo-local wrapper contract.
3. Add tests and register them in local CI.
4. Run pre-commit update/archive gate, OpenSpec guard, unit tests, local gate, and local MR review.
5. Archive the completed OpenSpec change as one local integration package before merging to local `main`.

## Rollback plan

Revert the local commit or reset local `main` to the rollback ref created before merge. Since no user-level files are written, rollback is repository-only.

## Validation path

- `python test/chrome_devtools_mcp_managed.test.py` - runs the focused managed-wrapper unit tests.
- `python tools/chrome_devtools_mcp_managed.py isolated-session plan --project pythonproject-langgraph --session smoke --purpose smoke --json` - verifies plan output stays dry-run and sanitized.
- `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> isolated-session reserve --project pythonproject-langgraph --session smoke --purpose smoke --json` - verifies lease and wrapper receipt writes in an isolated test state directory.
- `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> isolated-session start --project pythonproject-langgraph --session smoke --purpose smoke --json` - verifies live start fails closed without an install receipt.
- `python tools/check_precommit_update_archive.py --root . --json` - verifies the pre-commit update/archive gate.
- `python tools/run_openspec_guard.py --root . --json` - verifies OpenSpec guard health.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 300` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -BaseRef main -HeadRef HEAD` - runs the local MR review gate.
