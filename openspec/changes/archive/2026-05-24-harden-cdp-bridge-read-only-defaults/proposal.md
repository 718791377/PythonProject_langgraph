## Why

The user-level MCP, skills, browser, and CLI governance plan requires CDP Bridge to remain inspect-first. The previous browser slices established owner registry and Chrome DevTools MCP managed wrapper behavior, but CDP Bridge still needed a repository-local guard that separates read-only inventory from sensitive read/write actions before any live adapter can be trusted.

## What Changes

- Add `tools/cdp_bridge_governance.py` as a repo-local governance guard for CDP Bridge action dispatch.
- Treat `tab.list`, `dom.scan`, `screenshot.capture`, and `inventory` as read-only actions that are allowed without owner or authorization evidence.
- Treat `cookie.read`, `js.evaluate`, `mouse.click`, `keyboard.type`, `page.navigate`, and unknown actions as sensitive actions that fail closed unless owner lease evidence and one-task authorization receipt evidence are present.
- Reuse the browser owner registry state contract without mutating it.
- Add tests for read-only allowance, sensitive-action fail-closed behavior, active owner plus authorization success, unknown-action blocking, and output redaction.
- Register the new test in the shared CI manifest and update the bilingual implementation plan plus stable OpenSpec requirement.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-mcp-skills-browser-cli-governance`: add CDP Bridge read-only default and sensitive-action owner/authorization gating evidence.

## Impact

- Affected source: `tools/cdp_bridge_governance.py`.
- Affected tests: `test/cdp_bridge_governance.test.py`, `tools/ci/ci_test_manifest.json`.
- Affected governance docs: bilingual implementation plan and OpenSpec delta/stable spec surfaces.
- No user-level files under `C:\Users\lenovo\.codex` are modified by this slice.
- No Chrome instance is launched, no CDP endpoint is contacted, no cookie is read, and no click/type/navigate action is executed by this slice.

## Mainline classification

Existing mainline: user-level MCP, skills, browser automation, and CLI harness governance.

## Explicit non-goals

- Do not implement live CDP Bridge dispatch.
- Do not install or replace a user-level CDP Bridge wrapper.
- Do not launch Chrome, connect to CDP, click, type, navigate, evaluate JavaScript, read cookies, inspect user-owned browser data, or modify `C:\Users\lenovo\.codex\config.toml`.
- Do not implement OpenCLI enforcement in this slice.

## Rollout sequence

1. Add OpenSpec artifacts for the CDP Bridge read-only-default guard slice.
2. Add the repo-local CDP Bridge governance helper with non-mutating action classification.
3. Add focused tests for read-only allowance and sensitive-action fail-closed behavior.
4. Register the new test in the shared CI manifest.
5. Run pre-commit update/archive gate, OpenSpec guard, focused unit tests, local gate, and local MR review.
6. Archive the completed OpenSpec change as one local integration package before merging to local `main`.

## Rollback plan

Revert the local commit or reset local `main` to the rollback ref created before merge. Since no user-level files are written, rollback is repository-only.

## Validation path

- `python test/cdp_bridge_governance.test.py` - verifies CDP Bridge read-only and sensitive-action gating behavior.
- `python tools/cdp_bridge_governance.py --state-dir <tmp> check --action tab.list --target tab:debug-1 --session session-a --json` - smokes read-only allowance without dispatching CDP.
- `python tools/cdp_bridge_governance.py --state-dir <tmp> check --action cookie.read --target tab:debug-1 --session session-a --json` - smokes sensitive-action fail-closed behavior without reading cookies.
- `python tools/check_precommit_update_archive.py --root . --json` - enforces the pre-commit update/archive gate.
- `python tools/run_openspec_guard.py --root . --json` - verifies OpenSpec and repository governance guards.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 300` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -BaseRef main -HeadRef HEAD` - runs local MR review before main integration.
