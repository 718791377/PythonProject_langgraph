# Proposal: enforce oh-my-pi sidecar receipt guard

## Why

The user-level MCP/skills/browser/CLI governance plan keeps `oh-my-pi` as a
reference sidecar until pinned install/update receipts, smoke evidence, and
rollback pointers are present. The repository needs a deterministic guard for
that evidence before any user-level clone, wrapper, or update flow is allowed.

## What

- Add a repo-local `oh_my_pi_sidecar_governance.py` helper that writes and
  validates sanitized install/update receipts without installing or running
  `oh-my-pi`.
- Require immutable pins, passing smoke evidence, update rollback pointers, and
  non-active sidecar status.
- Add tests for install receipt writing, unpinned-ref blocking, update smoke
  gating, update rollback evidence, and receipt validation.
- Promote the receipt/update/rollback contract into the stable governance spec.

## Non-goals

- Do not clone `oh-my-pi`.
- Do not install user-level wrappers.
- Do not edit `C:\Users\lenovo\.codex\config.toml`.
- Do not run `oh-my-pi`, perform network fetches, or hard-load skills.
- Do not implement CLI-Anything or `wecom-cli`.
