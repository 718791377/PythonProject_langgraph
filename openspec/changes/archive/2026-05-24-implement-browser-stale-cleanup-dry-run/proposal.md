## Why

The user-level MCP, skills, browser, and CLI governance plan requires browser automation cleanup to be evidence-first and fail-safe. The previous slices implemented browser owner leases and `chrome-devtools-mcp` profile modes, but the managed wrapper still needed a safe stale scan and cleanup dry-run surface before any later real cleanup can be considered.

## What Changes

- Extend `tools/chrome_devtools_mcp_managed.py` with wrapper-level `stale-scan --dry-run` and `cleanup dry-run` commands.
- Delegate stale detection and cleanup candidate classification to `tools/browser_owner_registry.py`.
- Keep wrapper cleanup as dry-run only: no profile deletion, no browser launch, no CDP connection, no user-level Codex config mutation, and no cookie/browser data reads.
- Keep project profiles and human-delegated / human-owned assets protected from cleanup.
- Add tests covering wrapper stale scan, cleanup dry-run, project-profile retention, human protection, and cleanup non-mutation.
- Update the bilingual implementation plan and stable OpenSpec requirements.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-mcp-skills-browser-cli-governance`: add wrapper-level stale scan and cleanup dry-run evidence for the browser automation lane.

## Impact

- Affected source: `tools/chrome_devtools_mcp_managed.py`.
- Affected tests: `test/chrome_devtools_mcp_managed.test.py`, `test/browser_owner_registry.test.py`.
- Affected governance docs: bilingual implementation plan and OpenSpec delta/stable spec surfaces.
- No user-level files under `C:\Users\lenovo\.codex` are modified by this slice.
- No Chrome instance is launched, no CDP endpoint is contacted, and no profile directory is deleted by this slice.

## Mainline classification

Existing mainline: user-level MCP, skills, browser automation, and CLI harness governance.

## Explicit non-goals

- Do not implement real cleanup execution.
- Do not install or replace the user-level `chrome-devtools-mcp` wrapper.
- Do not launch Chrome, connect to CDP, click/type/navigate, read cookies, inspect user-owned browser data, or modify `C:\Users\lenovo\.codex\config.toml`.
- Do not implement CDP Bridge/OpenCLI enforcement, `oh-my-pi`, CLI-Anything, or `wecom-cli` in this slice.

## Rollout sequence

1. Add OpenSpec artifacts for the stale-scan and cleanup dry-run wrapper slice.
2. Extend the repo-local wrapper with non-mutating maintenance commands.
3. Add focused tests for cleanup candidate classification and protected profile behavior.
4. Run pre-commit update/archive gate, OpenSpec guard, focused unit tests, local gate, and local MR review.
5. Archive the completed OpenSpec change as one local integration package before merging to local `main`.

## Rollback plan

Revert the local commit or reset local `main` to the rollback ref created before merge. Since no user-level files are written, rollback is repository-only.

## Validation path

- `python test/browser_owner_registry.test.py` - verifies owner-registry stale and cleanup-dry-run behavior.
- `python test/chrome_devtools_mcp_managed.test.py` - verifies wrapper command behavior and safety evidence.
- `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> stale-scan --dry-run --json` - smokes the wrapper stale-scan surface.
- `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> cleanup dry-run --json` - smokes the wrapper cleanup preview surface.
- `python tools/check_precommit_update_archive.py --root . --json` - enforces the pre-commit update/archive gate.
- `python tools/run_openspec_guard.py --root . --json` - verifies OpenSpec and repository governance guards.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 300` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -BaseRef main -HeadRef HEAD` - runs local MR review before main integration.
