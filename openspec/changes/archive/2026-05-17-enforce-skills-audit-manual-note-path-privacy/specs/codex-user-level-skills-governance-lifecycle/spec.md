## ADDED Requirements

### Requirement: Skills usage audit reports SHALL sanitize manual-note source paths

The skills usage audit report SHALL sanitize and bound manual-note source paths before retaining them in `manual_evidence.invalid_notes`, candidate source references, or sanitized Markdown summaries.

Manual-note source paths SHALL NOT be treated as retained raw evidence. They SHALL redact private Windows paths, POSIX home paths, UNC shares, access tokens, API keys, cookies, standalone secrets, and similar sensitive substrings before report retention.

#### Scenario: Manual note path contains a private path or secret

- **WHEN** a manual-note file path is missing, invalid, or otherwise included in invalid-note metadata
- **AND** that path contains a private path, token, cookie, or secret-like value
- **THEN** the audit report SHALL retain only a redacted and bounded path placeholder
- **AND** the raw private path, token, cookie, or secret-like value SHALL NOT appear in report JSON or sanitized Markdown summaries

#### Scenario: Manual evidence contract is incomplete or unsanitized

- **WHEN** the report field contract validates a generated or candidate-source audit report
- **AND** `manual_evidence` omits source-path privacy fields, marks source paths as retained, contains raw private paths or secrets, or permits overlong retained path values
- **THEN** the field contract SHALL fail
- **AND** the report SHALL be treated as incomplete evidence until regenerated or the script is fixed
