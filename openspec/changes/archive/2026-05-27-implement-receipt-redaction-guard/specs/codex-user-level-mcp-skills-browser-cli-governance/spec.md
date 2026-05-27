# Delta: receipt redaction guard

## ADDED Requirements

### Requirement: User-level receipt governance guard SHALL validate authorization, update, rollback, and redaction evidence

The repository SHALL provide a repo-local generic receipt governance guard for user-level MCP, skills, browser, and CLI harness lanes. The guard SHALL validate one-task authorization receipt schema, update receipt schema, rollback pointer presence, smoke evidence, and redaction boundaries without installing tools, calling MCP servers, controlling browsers, reading browser data, mutating user-level Codex configuration, or emitting raw private paths or raw secrets in default output.

#### Scenario: Authorization receipt is missing required fields

- **WHEN** `python tools/user_level_receipt_governance.py auth-check --receipt <path> --action browser.click --target tab:123 --session session-a --json` runs on an incomplete receipt
- **THEN** the command SHALL fail closed
- **AND** it SHALL report missing authorization receipt fields

#### Scenario: Valid update receipt hashes private paths and rollback pointer

- **WHEN** `update-check` receives a valid update receipt with install, wrapper, state, smoke, updater, owner-lane, redaction, and rollback evidence
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `rollback_ready=true`
- **AND** it SHALL emit hashes for install path, wrapper path, state path, and rollback pointer

#### Scenario: Redaction check detects raw sensitive payloads

- **WHEN** `python tools/user_level_receipt_governance.py redact-check --receipt <path> --json` runs on a receipt containing cookies, inline token values, message contents, or plugin description dumps
- **THEN** the command SHALL fail closed
- **AND** it SHALL report redaction findings

