## MODIFIED Requirements

### Requirement: Skills usage audit warning triage SHALL expose skipped-loading source review

The Skills usage audit warning-triage report SHALL expose skipped-loading warning counts and the review policy for invalid or skipped skills.

`warning_triage` MUST include `skipped_loading_count`, `recent_skipped_loading_samples`, and `skipped_loading_review`. Skipped-loading samples retained in `log_evidence.recent_skipped_loading` MUST remain sanitized. The review policy MUST direct the operator to record the source first and avoid vendor-cache bulk edits unless explicitly authorized.

#### Scenario: Skipped-loading warning is present during triage

- **WHEN** `--warning-triage` scans logs containing `Skipped loading` warnings
- **THEN** the report SHALL include skipped-loading counts and sample counts in `warning_triage`
- **AND** sanitized Markdown summaries SHALL render the skipped-loading triage state
- **AND** raw private paths or secrets from skipped-loading log messages SHALL NOT appear in retained report evidence

#### Scenario: Skipped-loading triage fields are missing

- **WHEN** the report field contract validates warning triage
- **AND** skipped-loading count, sample count, or review policy fields are missing or malformed
- **THEN** the field contract SHALL fail
- **AND** profile-candidate generation SHALL remain blocked until the report is regenerated or the script is fixed
