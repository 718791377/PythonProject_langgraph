## ADDED Requirements

### Requirement: Skills usage audit log excerpts SHALL preserve redaction marker integrity

The skills usage audit report SHALL preserve complete redaction markers when sanitized log excerpts are truncated for retention.

Sanitized log excerpts MUST redact private paths, access tokens, API keys, cookies, standalone secrets, and similar sensitive substrings before truncation. If truncation reaches the middle of a redaction marker, the retained excerpt MUST include a complete redaction marker and MUST NOT retain a partial marker such as `[RE`, `[REDACTED_`, or `[REDACTED_SE` as the only privacy indication.

#### Scenario: Log excerpt truncates across a redacted private path

- **WHEN** a budget-warning log message contains a private path near the excerpt limit
- **THEN** the retained `message_excerpt` SHALL include either no path marker or a complete `[REDACTED_PATH]` marker
- **AND** it SHALL NOT include the raw private path
- **AND** it SHALL NOT end with a partial redaction marker fragment

#### Scenario: Log excerpt truncates across a redacted secret

- **WHEN** a budget-warning log message contains a secret-like value near the excerpt limit
- **THEN** the retained `message_excerpt` SHALL include either no secret marker or a complete `[REDACTED_SECRET]` marker
- **AND** it SHALL NOT include the raw secret value
- **AND** it SHALL NOT end with a partial redaction marker fragment
