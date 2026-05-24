## Why

The user-level MCP, skills, browser, and CLI governance plan requires `chrome-devtools-mcp` to support both temporary isolated sessions and long-lived project profiles. The previous managed-wrapper slice modeled isolated-session behavior only. This slice adds the repository-local project-profile contract without installing user-level wrappers, starting Chrome, connecting to CDP, or reading user browser data.

## What Changes

- Extend `tools/chrome_devtools_mcp_managed.py` with `project-profile plan`, `reserve`, `start`, `release`, and `status` commands.
- Use the `codex-managed-project` owner class for project profiles.
- Require project-profile authorization receipts before reserve and live start attempts.
- Keep project profiles long-lived and protected from cleanup by setting `cleanup_allowed_after_stale_evidence=false`.
- Keep live start fail-closed: no authorization fails first, missing install receipt fails second, and even with both receipts live startup remains deferred in the repo-local MVP.
- Add focused unit tests for project-profile dry-run planning, authorization failure, protected lease writing, same-profile exclusivity, live-start gates, and release receipts.
- Update bilingual implementation-plan state and stable OpenSpec requirements.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-mcp-skills-browser-cli-governance`: extend the repo-local `chrome-devtools-mcp` managed wrapper MVP with project-profile gating and retention behavior.

## Impact

- Affected source: `tools/chrome_devtools_mcp_managed.py`.
- Affected tests: `test/chrome_devtools_mcp_managed.test.py`.
- Affected governance docs: bilingual implementation plan and OpenSpec delta/stable spec surfaces.
- No user-level files under `C:\Users\lenovo\.codex` are modified by this slice.
- No Chrome instance is launched and no CDP endpoint is contacted by this slice.

## Mainline classification

Existing mainline: user-level MCP, skills, browser automation, and CLI harness governance.

## Explicit non-goals

- Do not install or replace the user-level `chrome-devtools-mcp` wrapper.
- Do not launch Chrome, connect to CDP, click/type/navigate, read cookies, inspect user-owned browser data, or modify `C:\Users\lenovo\.codex\config.toml`.
- Do not implement stale cleanup dry-run or cleanup execution in this slice.
- Do not implement CDP Bridge/OpenCLI enforcement, `oh-my-pi`, CLI-Anything, or `wecom-cli` in this slice.
- Do not delete project-profile directories. Project profiles remain protected long-lived assets.

## Rollout sequence

1. Add OpenSpec artifacts for the `chrome-devtools-mcp` project-profile managed-wrapper MVP slice.
2. Extend the repo-local wrapper contract.
3. Add focused tests for project-profile authorization and retention behavior.
4. Run pre-commit update/archive gate, OpenSpec guard, unit tests, local gate, and local MR review.
5. Archive the completed OpenSpec change as one local integration package before merging to local `main`.

## Rollback plan

Revert the local commit or reset local `main` to the rollback ref created before merge. Since no user-level files are written, rollback is repository-only.

## Validation path

- `python test/chrome_devtools_mcp_managed.test.py` - runs the focused managed-wrapper unit tests.
- `python tools/chrome_devtools_mcp_managed.py project-profile plan --project pythonproject-langgraph --profile dev-login --session smoke --purpose smoke --json` - verifies plan output stays dry-run and sanitized.
- `python tools/check_precommit_update_archive.py --root . --json` - verifies the pre-commit update/archive gate.
- `python tools/run_openspec_guard.py --root . --json` - verifies OpenSpec guard health.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 300` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -BaseRef main -HeadRef HEAD` - runs the local MR review gate.
