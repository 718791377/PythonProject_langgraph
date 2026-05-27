# Design: receipt redaction guard

## Approach

Use one deterministic Python helper with three fail-closed checks:

- `auth-check` validates one-task authorization receipts.
- `update-check` validates update receipts, smoke evidence, owner lane, and rollback pointer.
- `redact-check` detects raw sensitive payloads.

The helper returns sanitized JSON and never performs live operations.

