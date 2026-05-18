## ADDED Requirements

### Requirement: Skills usage audit Markdown summaries SHALL expose audit-state blockers

The skills usage audit sanitized Markdown summary SHALL expose the audit-state next action, profile-apply allowance, and any state-machine blockers that explain why the report cannot advance.

The Markdown summary MUST render blockers from `close_blockers`, `candidate_blockers`, `summary_review_blockers`, `pause_blockers`, and `warning_triage_blockers`. When no audit-state blocker exists, the summary MUST render `none`.

#### Scenario: Reviewer reads a blocked closure summary

- **WHEN** the audit script generates a sanitized Markdown summary for a report whose closure is blocked
- **THEN** the Markdown SHALL show the audit state's next action
- **AND** it SHALL show that profile apply is not allowed
- **AND** it SHALL list the concrete closure blockers without requiring the reviewer to open raw JSON

#### Scenario: Reviewer reads a closed or unblocked summary

- **WHEN** the audit script generates a sanitized Markdown summary for a report with no audit-state blockers
- **THEN** the Markdown SHALL show `none` for audit-state blockers
