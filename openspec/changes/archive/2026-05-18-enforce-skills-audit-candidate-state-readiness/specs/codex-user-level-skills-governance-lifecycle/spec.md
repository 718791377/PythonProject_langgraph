## ADDED Requirements

### Requirement: Skills usage audit profile-candidate gates SHALL require candidate-ready audit states

The Skills usage audit profile-candidate gate SHALL only allow candidate preview records from audit states that are ready for candidate review.

Candidate-ready audit states MUST be limited to `summary-reviewed`, `apply-candidate`, and `closed-with-candidate`. `planned`, `paused`, `running`, `ready-for-summary`, and `closed-no-change` MUST block candidate generation even when the caller supplies source-report paths, `--summary-reviewed`, and a target profile.

#### Scenario: Candidate gate receives a not-ready audit state

- **WHEN** profile-candidate generation validates an audit report
- **AND** `audit_state.state` is not one of `summary-reviewed`, `apply-candidate`, or `closed-with-candidate`
- **THEN** the candidate generation gate SHALL remain blocked with an audit-state readiness blocker
- **AND** the candidate SHALL remain preview-only, non-mutating, and not usable as apply authorization evidence
