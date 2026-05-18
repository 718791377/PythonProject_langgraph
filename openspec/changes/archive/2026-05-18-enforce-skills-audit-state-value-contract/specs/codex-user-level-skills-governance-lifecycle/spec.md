### Requirement: Skills usage audit field contracts SHALL validate audit-state values

The Skills usage audit report field contract SHALL validate that `audit_state` stays within the audit-only state machine and cannot be used as profile-apply authorization.

`audit_state.state` MUST be one of `planned`, `running`, `paused`, `ready-for-summary`, `summary-reviewed`, `apply-candidate`, `closed-no-change`, or `closed-with-candidate`. `audit_state.profile_apply_allowed` MUST be `false`. When present, `close_blockers`, `candidate_blockers`, `summary_review_blockers`, `pause_blockers`, and `warning_triage_blockers` MUST be lists of strings.

#### Scenario: Candidate gate receives an invalid audit state

- **WHEN** profile-candidate generation validates an audit report
- **AND** `audit_state.state` is unknown, `profile_apply_allowed` is not false, or an audit-state blocker field is not a string list
- **THEN** the field contract SHALL fail
- **AND** candidate generation SHALL remain blocked until the report is regenerated or the script is fixed
