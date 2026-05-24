## Why

The user-level governance plan requires `skills2cli` as the low-token, low-risk discovery surface for Codex skills before broader MCP/browser/CLI harness work continues. This slice implements the repository-local MVP so skill discovery, profile suggestions, and warnings can be inspected without hard-loading or dumping plugin skill bodies into model context.

## What Changes

- Add a repo-local `tools/skills2cli.py` helper with `index`, `search`, `show`, `profile suggest`, and `audit warnings` JSON commands.
- Keep default output compact and sanitized; full skill body output is excluded by default and available only through an explicit `--full` flag.
- Add tests for compact output, privacy redaction, profile suggestion non-apply behavior, and warning audit summaries.
- Register the new test in the local CI manifest.
- Update the user-level MCP/skills/browser/CLI governance plan to mark the `skills2cli` MVP implementation items complete.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-mcp-skills-browser-cli-governance`: add executable `skills2cli` MVP behavior for compact skill index/search/show, preview-only profile suggestion, and sanitized warning audit summaries.

## Impact

- Affected source: `tools/skills2cli.py`.
- Affected tests: `test/skills2cli.test.py`, `tools/ci/ci_test_manifest.json`.
- Affected governance docs: bilingual implementation plan and OpenSpec delta/stable spec surfaces.
- No user-level `C:\Users\lenovo\.codex` files are modified by this slice; user-level wrapper installation remains a later governed slice.

## Mainline classification

Existing mainline: user-level MCP, skills, browser automation, and CLI harness governance.

## Explicit non-goals

- Do not install or modify user-level wrapper files.
- Do not apply, disable, or hard-load skill profiles.
- Do not edit plugin cache SKILL.md files.
- Do not implement `mcp2cli`, browser owner registry, OpenCLI enforcement, CLI-Anything, `oh-my-pi`, or `wecom-cli` in this slice.

## Rollout sequence

1. Add OpenSpec artifacts for the `skills2cli` MVP slice.
2. Implement the repo-local helper and tests.
3. Register tests in local CI.
4. Run pre-commit update/archive gate, OpenSpec guard, unit tests, local gate, and local MR review.
5. Archive the completed OpenSpec change as one local integration package before merging to local `main`.

## Rollback plan

Revert the local commit or reset local `main` to the rollback ref created before merge. Since no user-level files are written, rollback is repository-only.

## Validation path

- `python test/skills2cli.test.py` - runs the focused skills2cli unit tests.
- `python tools/skills2cli.py index --json` - verifies compact skill indexing.
- `python tools/skills2cli.py search plugin --json` - verifies compact skill search.
- `python tools/skills2cli.py profile suggest --task "debug chrome skills context warning" --json` - verifies preview-only profile advice.
- `python tools/skills2cli.py audit warnings --since 7d --json` - verifies warning audit summaries.
- `python tools/check_precommit_update_archive.py --root . --json` - verifies the pre-commit update/archive gate.
- `python tools/run_openspec_guard.py --root . --json` - verifies OpenSpec guard health.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -BaseRef main -HeadRef HEAD` - runs the local MR review gate.
