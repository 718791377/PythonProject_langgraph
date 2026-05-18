## ADDED Requirements

### Requirement: Skills usage audit reports SHALL expose script capability boundaries

The skills usage audit report SHALL expose what the audit helper can reliably cover and what still requires human review.

The JSON report MUST include `script_capability_boundaries` with non-empty `policy`, `reliable_coverage`, `human_review_required_for`, and `enhancement_triggers` fields. The field contract MUST fail when those fields are missing, wrong-typed, or empty. The sanitized Markdown summary MUST render the same boundary so reviewers do not treat the audit helper as an omniscient source of truth.

#### Scenario: Reviewer reads script capability boundaries in a generated report

- **WHEN** the audit script generates JSON and Markdown summary output
- **THEN** the JSON SHALL include non-empty script capability boundary lists
- **AND** the Markdown summary SHALL show reliable coverage, human-review needs, and enhancement triggers
- **AND** the field contract SHALL pass only when those boundary fields are present and non-empty

#### Scenario: Candidate gate receives a report without script boundaries

- **WHEN** profile-candidate generation validates an audit report
- **AND** `script_capability_boundaries` is missing, wrong-typed, or contains empty boundary lists
- **THEN** the field contract SHALL fail
- **AND** candidate generation SHALL remain blocked until the report is regenerated or the script is fixed
