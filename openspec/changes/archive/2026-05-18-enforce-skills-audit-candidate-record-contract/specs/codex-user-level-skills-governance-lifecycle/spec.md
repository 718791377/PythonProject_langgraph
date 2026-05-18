## ADDED Requirements

### Requirement: Skills usage audit profile candidates SHALL validate retained candidate records

The Skills usage audit helper SHALL attach a candidate-record contract to every generated profile apply candidate preview so retained JSON and Markdown artifacts cannot be mistaken for approval, applied state, or an unsafe configuration mutation.

The candidate-record contract MUST require the candidate's core fields, `approval_state=preview-only`, `mutates_config=false`, `edits_plugin_cache=false`, `hard_load_apply_performed=false`, explicit-authorization flags, `source_reports_privacy.status=passed`, a structured `candidate_generation_gate.allowed/blockers`, `rollback_path.restore_command`, `rollback_path.restart_required`, and a non-empty validation plan. If any of those fields are missing, malformed, unsafe, or retain raw private paths or secrets, the contract MUST fail and the candidate MUST NOT be treated as apply-ready evidence.

#### Scenario: Candidate preview carries a valid self-contract

- **WHEN** the audit script generates a profile apply candidate preview
- **THEN** the candidate SHALL include `candidate_record_contract.status=passed`
- **AND** the Markdown candidate summary SHALL render the candidate-record contract status and blockers
- **AND** the candidate SHALL remain preview-only, non-mutating, and not usable as apply authorization evidence

#### Scenario: Candidate preview record is malformed or unsafe

- **WHEN** a candidate record is missing required fields, uses `approval_state` other than `preview-only`, marks config/plugin/hard-load mutation as performed, has failed source-report privacy, has malformed gate blockers, lacks rollback restore information, or lacks validation steps
- **THEN** the candidate-record contract SHALL fail with blockers identifying the broken field
- **AND** the candidate SHALL remain blocked until regenerated or the script is fixed
