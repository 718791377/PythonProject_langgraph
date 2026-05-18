## MODIFIED Requirements

### Requirement: Skills usage audit profile candidates SHALL require explicit target profiles

The Skills usage audit profile-candidate gate SHALL require an explicit target profile before candidate JSON or Markdown can be treated as a usable preview.

`--candidate-output`, `--candidate-summary-output`, and `--close-audit with-candidate` MUST require `--target-profile`. The audit helper MUST NOT infer the target profile from the current enabled profile, candidate filename, or generic continuation. When the target profile is missing, the report or candidate gate MUST remain blocked with `target_profile_missing`, keep profile apply disallowed, and avoid mutating `config.toml`, plugin cache, or hard-load state.

#### Scenario: Candidate output is requested without a target profile

- **WHEN** the audit script is asked to generate a profile candidate with `--candidate-output` or `--candidate-summary-output`
- **AND** `--target-profile` is missing or blank
- **THEN** the audit state or candidate generation gate SHALL report `target_profile_missing`
- **AND** the candidate SHALL remain `preview-only`, blocked, non-mutating, and not usable as apply approval evidence

#### Scenario: Audit closure with candidate lacks a target profile

- **WHEN** `--close-audit with-candidate` is requested
- **AND** the target profile is missing or blank
- **THEN** the closure SHALL be blocked with `target_profile_missing`
- **AND** the report SHALL remain non-mutating until a reviewed candidate is regenerated with an explicit target profile
