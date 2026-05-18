## MODIFIED Requirements

### Requirement: Skills usage audit manual evidence SHALL expose conflict review state

The Skills usage audit report SHALL expose whether manual evidence includes exceptions, approved hard-load exceptions, or other manual judgments that require disposition before a profile decision.

`manual_evidence.conflict_review` MUST include status, policy, conflict/exception count, disposition-required flag, and disposition text. Manual notes MUST NOT override script evidence. If any manual note has `evidence_level=exception` or `action_taken=approved hard-load exception`, the conflict review status MUST require manual disposition and sanitized Markdown summaries MUST render that state.

#### Scenario: Manual exception note is present

- **WHEN** a sanitized manual evidence note records an exception or approved hard-load exception
- **THEN** the audit report SHALL set `manual_evidence.conflict_review.status=manual_conflict_or_exception_review_required`
- **AND** it SHALL render the conflict/exception count, non-override policy, and disposition requirement in the sanitized Markdown summary

#### Scenario: Manual conflict review fields are missing

- **WHEN** the report field contract validates manual evidence
- **AND** `manual_evidence.conflict_review` is missing, malformed, or carries an invalid policy or count
- **THEN** the field contract SHALL fail
- **AND** the report SHALL be treated as incomplete evidence until regenerated or the script is fixed
