## Why

The governance plan requires `mcp2cli` after the repo-local `skills2cli` MVP so MCP discovery can move through a compact, low-token profile registry before higher-risk browser, OpenCLI, and WeCom lanes are implemented. This slice adds the repository-local facade and fail-closed call policy without installing user-level wrappers or invoking sensitive MCP tools.

## What Changes

- Add a repo-local `tools/mcp2cli.py` helper with compact `list`, `search`, `show`, and guarded `call` JSON commands.
- Add a sanitized allowed-profile registry at `tools/mcp2cli_allowed_profiles.json`.
- Keep `list`, `search`, and default `show` output compact; full tool metadata requires the explicit `--full` option.
- Make `call` fail closed for sensitive or medium/high-risk tools unless an explicit authorization receipt is supplied.
- Add tests for profile registry shape, compact output, sensitive-call blocking, and authorization-receipt enforcement.
- Update the implementation plan checklist to mark the repo-local `mcp2cli` MVP items complete.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-mcp-skills-browser-cli-governance`: add executable repo-local `mcp2cli` MVP behavior for compact MCP profile discovery and fail-closed call gating.

## Impact

- Affected source: `tools/mcp2cli.py`, `tools/mcp2cli_allowed_profiles.json`.
- Affected tests: `test/mcp2cli.test.py`, `tools/ci/ci_test_manifest.json`.
- Affected governance docs: bilingual implementation plan and OpenSpec delta/stable spec surfaces.
- No user-level files under `C:\Users\lenovo\.codex` are modified by this slice; user-level wrapper installation remains a later governed slice.

## Mainline classification

Existing mainline: user-level MCP, skills, browser automation, and CLI harness governance.

## Explicit non-goals

- Do not install user-level `mcp2cli` wrapper files.
- Do not route through MCP Router or mutate Codex MCP configuration.
- Do not invoke browser, shell-capable, remote-infrastructure, payment/account, or personal-data tools.
- Do not implement the port allocator, browser owner registry, Chrome DevTools managed wrapper, CDP Bridge/OpenCLI enforcement, `oh-my-pi`, CLI-Anything, or `wecom-cli` in this slice.

## Rollout sequence

1. Add OpenSpec artifacts for the `mcp2cli` MVP slice.
2. Implement the repo-local registry and helper.
3. Add tests and register them in local CI.
4. Run pre-commit update/archive gate, OpenSpec guard, unit tests, local gate, and local MR review.
5. Archive the completed OpenSpec change as one local integration package before merging to local `main`.

## Rollback plan

Revert the local commit or reset local `main` to the rollback ref created before merge. Since no user-level files are written, rollback is repository-only.

## Validation path

- `python test/mcp2cli.test.py` - runs the focused mcp2cli unit tests.
- `python tools/mcp2cli.py list --profile core-readonly --json` - verifies compact profile listing.
- `python tools/mcp2cli.py search browser --profile browser-readonly --json` - verifies compact profile search.
- `python tools/mcp2cli.py show browser.tabs.list --profile browser-readonly --json` - verifies default compact show output.
- `python tools/mcp2cli.py call browser.tabs.list --profile browser-readonly --json --args {}` - verifies sensitive calls fail closed without authorization.
- `python tools/check_precommit_update_archive.py --root . --json` - verifies the pre-commit update/archive gate.
- `python tools/run_openspec_guard.py --root . --json` - verifies OpenSpec guard health.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -BaseRef main -HeadRef HEAD` - runs the local MR review gate.
