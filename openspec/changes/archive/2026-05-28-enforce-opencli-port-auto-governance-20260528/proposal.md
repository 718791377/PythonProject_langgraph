# Proposal: Enforce OpenCLI port-auto governance

## Why

The user-level MCP, skills, browser, and CLI governance plan states that OpenCLI must use allocator-driven `--port auto` and codex-port lease evidence. The repo-local OpenCLI governance guard already enforces on-demand mode, browser owner evidence, and sensitive-action authorization receipts, but it did not yet fail closed when a hard-coded OpenCLI port or missing port lease was supplied.

## What

- Extend `tools/opencli_governance.py` with an explicit port policy gate.
- Require `--port auto` for OpenCLI pre-dispatch checks.
- Require a sanitized `codex-port` lease receipt in the Codex browser/OpenCLI range `39300-39499`.
- Add unit tests proving missing port lease, hard-coded port, and wrong port range fail closed.
- Promote the behavior into the stable user-level MCP/skills/browser/CLI governance spec at archive.

## Non-goals

- Do not install, start, or update OpenCLI.
- Do not allocate live user-level ports outside fixture receipts.
- Do not mutate `C:\Users\lenovo\.codex`.
- Do not push remote branches or open remote MRs.

## Rollback

Rollback by reverting the local feature commit or resetting local `main` to the rollback ref created before integration. No user-level runtime state is changed.
