## MODIFIED Requirements

### Requirement: Skills usage audit reports SHALL expose output-retention status

Every Skills usage audit JSON report SHALL include the current output-retention gate status so reviewers can see whether local-only raw audit outputs are being kept out of Git without running a separate checker first.

The `output_retention` field MUST identify the checker, state whether the checker passed, state that `.tmp/` outputs and raw audit JSON reports are local-only, identify `sanitized_markdown_summary` as the long-term evidence format, and report the current violation count. The report field contract MUST fail if this status is missing, malformed, non-passing, or inconsistent with the local-only retention policy. Sanitized Markdown summaries MUST render the output-retention status and long-term evidence format.

#### Scenario: Reviewer reads an audit report

- **WHEN** the audit script generates a JSON report
- **THEN** the report SHALL include `output_retention.status`, `output_retention.ok`, `output_retention.checker`, `.tmp` local-only policy, raw JSON local-only policy, long-term evidence format, and violation count
- **AND** the field contract SHALL pass only when the output-retention gate is passing

#### Scenario: Reviewer reads a sanitized summary

- **WHEN** the audit script renders `--summary-output`
- **THEN** the Markdown SHALL show the output-retention gate status
- **AND** it SHALL show that long-term evidence must be `sanitized_markdown_summary`

#### Scenario: Candidate gate receives a report without retention status

- **WHEN** profile-candidate generation validates an audit report
- **AND** `output_retention` is missing, malformed, not passed, or does not preserve the local-only raw-output policy
- **THEN** the field contract SHALL fail
- **AND** candidate generation SHALL remain blocked until the report is regenerated or the checker issue is fixed
