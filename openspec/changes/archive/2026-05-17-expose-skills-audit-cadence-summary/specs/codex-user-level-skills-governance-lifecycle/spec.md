## ADDED Requirements

### Requirement: Skills usage audit reports SHALL expose cadence-review drift

The skills usage audit report SHALL expose whether the audit run is on cadence, late, or recovering missed weekly reports.

The JSON report MUST include `cadence_review` with `late_run`, `missed_weekly_runs`, and `weekly_report_review`. The field contract MUST fail when those fields are missing or wrong-typed, when `missed_weekly_runs` is not `null` or a non-negative integer, or when `late_run=true` omits an explicit missed-run count. The sanitized Markdown summary MUST render the cadence fields in the audit-window section.

#### Scenario: Reviewer reads cadence state in a generated summary

- **WHEN** the audit script generates JSON and Markdown summary output
- **THEN** the JSON SHALL include the cadence-review fields
- **AND** the Markdown summary SHALL show late-run status, missed weekly runs, and weekly-report review status
- **AND** the field contract SHALL pass only when the cadence-review fields are present and valid

#### Scenario: Candidate gate receives a report with invalid cadence state

- **WHEN** profile-candidate generation validates an audit report
- **AND** `cadence_review` is missing, wrong-typed, has a negative missed-run count, or marks `late_run=true` without a missed-run count
- **THEN** the field contract SHALL fail
- **AND** candidate generation SHALL remain blocked until the report is regenerated or the script is fixed
