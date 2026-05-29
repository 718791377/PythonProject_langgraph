# Receipt redaction guard design

## Decision

Implement a repo-local generic guard for authorization receipts, update receipts, rollback pointers, and redaction boundaries before any user-level install lane can be treated as active.

## Boundaries

- No user-level Codex configuration mutation.
- No external MCP call, browser control, or browser-data read.
- Default output hashes private paths and rollback pointers.
- Redaction fails closed on raw secrets, cookies, tokens, message contents, browser data, and plugin description dumps.

