## ADDED Requirements

### Requirement: Project MOE Phase 1 Readiness Output Exposes Evidence Summary

The Project MOE Phase 1 readiness checker SHALL expose stable top-level evidence summary fields for GUI preflight and rollout decisions.

#### Scenario: Ready Lane output includes evidence fields

- **GIVEN** a target project satisfies Phase 1 static and read-contract readiness
- **WHEN** the operator runs `check_project_moe_phase1_readiness.py --json`
- **THEN** the payload includes `adaptation_lane`, `blockers`, `warnings`, `checked_files`, `redacted_paths`, and `control_mode_allowed`
- **AND** `adaptation_lane` is `ready`
- **AND** `control_mode_allowed` is true
- **AND** `checked_files` contains records for the agent TOML, private prompt source, Mode CLI, wrappers, startup hooks, and operator docs.

#### Scenario: Static-only output warns that CLI evidence is missing

- **GIVEN** a target project satisfies the static readiness surface
- **WHEN** the operator runs `check_project_moe_phase1_readiness.py --static-only --json`
- **THEN** the payload includes a warning that read-contract CLI execution was skipped
- **AND** `control_mode_allowed` remains false.
