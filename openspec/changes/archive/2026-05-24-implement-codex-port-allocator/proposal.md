# Implement codex-port allocator MVP

## Why

The user-level MCP/skills/browser/CLI governance plan requires a small port allocator before browser automation and OpenCLI adapters can safely share ports across projects and sessions. Codex-managed ports must stay before external project ports, and allocation must fail closed rather than killing or stealing existing listeners.

## What

- Add a repo-local `tools/codex_port.py` helper implementing `lease reserve/renew/release/list/import-legacy/gc`.
- Add `tools/codex_port_ranges.json` with Codex and external project range ownership.
- Add unit tests for owner-range checks, pending leases, receipts, live-socket collision skipping, owner-session release protection, legacy import, and GC dry-run evidence.
- Promote stable OpenSpec requirements and update the bilingual implementation-plan checklist.

## Non-goals

- No user-level wrapper installation under `C:\Users\lenovo\.codex`.
- No persistent service launch.
- No OpenCLI or browser wrapper integration yet.
- No process killing or port-holder cleanup.

## Rollback

Revert the repository commit or reset local `main` to the pre-merge rollback ref. No user-level state is modified by this slice.
