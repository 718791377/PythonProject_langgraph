## ADDED Requirements

### Requirement: Project MOE Phase 1 Read Contract Rejects Unsupported Envelope Schema

The Project MOE Phase 1 readiness checker SHALL reject target Mode CLI read-contract JSON envelopes whose `schema_version` differs from the toolchain-supported schema version.

#### Scenario: Unsupported schema version fails closed

- **GIVEN** a target project otherwise satisfies the Phase 1 static readiness surface
- **AND** its read-only Mode CLI command emits a JSON envelope with `schema_version` not equal to the supported Project MOE GUI toolchain schema version
- **WHEN** the operator runs `check_project_moe_phase1_readiness.py --json` in execute-read-contract mode
- **THEN** the checker reports `ok=false`
- **AND** it returns the stable blocker `blocked:cli_envelope_schema_version_mismatch`
- **AND** `control_mode_allowed` remains false.

#### Scenario: Static-only mode still does not execute the target CLI

- **GIVEN** a target project has a Mode CLI that would emit an unsupported schema version if executed
- **WHEN** the operator runs the readiness checker with `--static-only --json`
- **THEN** the checker does not execute the target CLI
- **AND** the unsupported runtime schema is not treated as evidence either for or against control readiness.
