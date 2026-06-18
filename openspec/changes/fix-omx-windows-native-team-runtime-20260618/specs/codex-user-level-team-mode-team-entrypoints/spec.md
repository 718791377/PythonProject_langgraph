## ADDED Requirements

### Requirement: Automatic team Apply SHALL fail closed when operational preflight fails

`omx-team-auto.ps1 -Apply` SHALL perform operational preflight before mutating tracked team state or active selector state.

#### Scenario: Native OMX preflight fails on Windows

- **GIVEN** the automatic helper plans a `native_omx` worker team on Windows
- **AND** the runtime backend preflight returns `operational_ready=false`
- **WHEN** the operator runs `omx-team-auto.ps1 -Apply -Json`
- **THEN** the helper SHALL return a structured blocked result
- **AND** it SHALL NOT create or update `.omx/state/team/codex-auto-managed-team.json`
- **AND** it SHALL NOT write an active native selector as though a team is running.

### Requirement: Automatic team output SHALL expose runtime backend evidence

The automatic team helper SHALL include runtime backend evidence in both planning and apply output.

#### Scenario: Operator inspects automatic plan output

- **WHEN** the operator runs `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 2 -Json`
- **THEN** the output SHALL include `runtime_backend`, `preflight_passed`, `operational_ready`, and `blockers`
- **AND** wrapper existence alone SHALL NOT be reported as launch evidence.
