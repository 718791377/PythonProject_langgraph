# Proposal: enforce CLI-Anything install receipt boundary

## Why

The user-level MCP/skills/browser/CLI governance plan keeps CLI-Anything and CLI Hub as harness-generation support until pinned install/update receipts, smoke evidence, rollback pointers, and no-hard-load boundaries are present. The repository needs a deterministic guard before any user-level CLI-Anything installation, update, or harness-generation workflow is considered eligible.

## What

- Add a repo-local `cli_anything_governance.py` helper that writes and validates sanitized CLI-Anything install/update receipts without installing or running CLI-Anything.
- Require immutable pins, passing smoke evidence, update rollback pointers, and non-active statuses.
- Enforce the harness-generation-only boundary and block hard-loading bulk skills.
- Add tests for install receipt writing, hard-load blocking, update smoke gating, update rollback evidence, rollback planning, and harness planning.
- Promote the receipt/update/rollback and harness-boundary contract into the stable governance spec.

## Non-goals

- Do not clone CLI-Anything or CLI Hub resources.
- Do not install user-level wrappers.
- Do not edit `C:\Users\lenovo\.codex\config.toml`.
- Do not run CLI-Anything, perform network fetches, hard-load skills, or control WXWork.
- Do not implement `wecom-cli` live control.
