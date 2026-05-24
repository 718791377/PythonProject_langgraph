# Design: Startup Instruction Mojibake Scan

## Scope

The checker is intentionally narrower than a repository-wide mojibake linter. It covers the active surfaces that can affect startup behavior or operator routing decisions:

- `AGENTS.md` - primary repository instruction surface loaded during startup
- the bilingual startup summary pair
- governance policies referenced by AGENTS for startup, launcher payload, MCP scope, worktree isolation, LangGraph runtime, OpenSpec workflow, and orchestration activation behavior

Historical memory notes, archived OpenSpec changes, generated gate reports, caches, and broad documentation trees are out of scope for this guard.

## Detection Strategy

The checker reads each configured surface through `utf-8-sig`, then fails on:

- UTF-8 decode errors
- Unicode replacement characters
- runs of three or more question marks, which indicate lossy console or transcoding replacement in these authority surfaces
- generated legacy-encoding mojibake variants of key Chinese startup/orchestration terms and the canary markers

The key Chinese tokens are generated from code points where needed so the script does not depend on copying the literal canary marker text into policy prose.

## Guard Integration

`tools/run_openspec_guard.py` runs the checker directly after the canary-surface checker, so canary placement and broader startup/instruction encoding integrity fail in the same guard sequence. The unittest is registered in `tools/ci/ci_test_manifest.json` so local gate coverage exercises the failure modes.
