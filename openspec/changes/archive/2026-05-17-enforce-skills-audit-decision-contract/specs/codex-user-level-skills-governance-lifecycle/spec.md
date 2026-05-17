## ADDED Requirements

### Requirement: Skills usage audit field contracts SHALL validate advisory decision recommendations

The skills usage audit report field contract SHALL validate that `decision_recommendation` remains an advisory-only, non-mutating review input.

The JSON report MUST include `decision_recommendation.status=advisory_only_no_profile_apply`, a non-empty policy string, `profile_apply_allowed=false`, the four required bucket lists (`profile_review_candidates`, `on_demand_soft_load`, `manual_review_medium_or_weak`, and `dormant_restorable`), and `bucket_counts` values that exactly match those bucket lengths. The field contract MUST fail when those fields are missing, wrong-typed, non-advisory, allow profile apply, contain non-string bucket entries, or carry stale bucket counts.

#### Scenario: Candidate gate receives a report with invalid decision recommendations

- **WHEN** profile-candidate generation validates an audit report
- **AND** `decision_recommendation` is missing, non-advisory, marks profile apply as allowed, omits a required bucket, includes a non-string bucket entry, or has a stale `bucket_counts` value
- **THEN** the field contract SHALL fail
- **AND** candidate generation SHALL remain blocked until the report is regenerated or the script is fixed
