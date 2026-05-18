## ADDED Requirements

### Requirement: Skills usage audit warning triage field contract SHALL enforce value-level semantics

The Skills usage audit warning-triage field contract SHALL validate the allowed values and cross-field semantics needed for profile decisions.

`warning_triage.status` MUST be one of `not_requested`, `blocked`, `log_source_unavailable`, `warning_found`, or `no_warning_found_in_triage_window`. `warning_triage.window_policy` MUST equal `use_days_1_or_since_for_warning_triage`. `warning_triage.skipped_loading_review` MUST be either `none` or `record_source_and_do_not_edit_vendor_cache_without_authorization`. `warning_triage.blockers` MUST be a list of known string blockers, currently only `warning_triage_window_not_narrow`. A blocked triage status MUST include at least one blocker, a non-blocked status MUST NOT retain blockers, and warning / skipped-loading count fields MUST be non-negative integers.

#### Scenario: Warning triage contains an invalid decision value

- **WHEN** the report field contract validates `warning_triage`
- **AND** the status, window policy, skipped-loading review, blocker list, blocker/status pairing, or warning/skipped-loading count value violates the allowed-value contract
- **THEN** the field contract SHALL fail with a `warning_triage:*` blocker
- **AND** profile-candidate generation SHALL remain blocked until the report is regenerated or the script is fixed
