## ADDED Requirements

### Requirement: Skills usage audit reports SHALL sanitize explicit-skill noise tokens

The skills usage audit report SHALL sanitize and bound tokens that were rejected from explicit skill evidence before retaining them in `session_evidence.explicit_skill_noise_removed` or `noise_review.explicit_skill_noise_removed`.

Rejected explicit-skill noise tokens SHALL NOT be counted as strong evidence. They SHALL redact private paths, access tokens, API keys, cookies, standalone secrets, and similar sensitive substrings before report retention. They SHALL be truncated to a fixed maximum length.

#### Scenario: Noise token contains a private path or secret

- **WHEN** a session transcript contains an explicit-skill announcement candidate that is rejected as generic or unknown noise
- **AND** that rejected token contains a private path, token, cookie, or secret-like value
- **THEN** the audit report SHALL retain only a redacted and bounded noise token
- **AND** the raw private path, token, cookie, or secret-like value SHALL NOT appear in report JSON or sanitized Markdown summaries

#### Scenario: Noise review contract is incomplete or unsanitized

- **WHEN** the report field contract validates a generated or candidate-source audit report
- **AND** `noise_review` omits its privacy fields, retains raw noise tokens, contains raw private paths or secrets, or permits overlong noise tokens
- **THEN** the field contract SHALL fail
- **AND** the report SHALL be treated as incomplete evidence until regenerated or the script is fixed
