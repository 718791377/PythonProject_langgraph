## ADDED Requirements

### Requirement: Startup launchers SHALL pass generated model instructions through a file reference

User-level startup launchers SHALL keep generated model-instruction bodies out of command-line startup overrides.

When a generated instruction body is required for wrapped Codex startup, the launcher support layer SHALL write that body to a managed UTF-8 state file and SHALL pass only a short `model_instructions_file` reference on the command line.

The startup argument builder SHALL NOT pass inline `developer_instructions` startup overrides for generated user-level orchestration instructions.

The repository SHALL keep an executable checker that validates the source launcher generator for this file-backed transport pattern and that checker SHALL be included in the aggregate OpenSpec guard.

#### Scenario: Wrapped startup carries generated instructions safely

- **WHEN** the generated launcher needs user-level team-mode model instructions
- **THEN** it SHALL write those instructions to a managed UTF-8 model-instructions file
- **AND** it SHALL pass exactly one short `model_instructions_file` startup override
- **AND** it SHALL forward that startup override before user-supplied arguments

#### Scenario: Inline generated developer instructions are reintroduced

- **WHEN** the startup argument builder or generated launcher attempts to pass `developer_instructions=` as a command-line override for generated startup instructions
- **THEN** the launcher payload context-boundary checker SHALL fail
- **AND** the aggregate OpenSpec guard SHALL report the launcher payload boundary violation