# Project MOE Mode CLI Timeout Budget

## ADDED Requirements

### Requirement: Mode CLI invocations SHALL use a configurable bounded timeout budget

Project MOE GUI Mode CLI subprocess calls SHALL use a bounded timeout budget that defaults to 60 seconds and MAY be overridden by the `PROJECT_MOE_GUI_MODE_CLI_TIMEOUT_SECONDS` environment variable when the variable contains a positive numeric value.

#### Scenario: Read-contract call uses explicit environment budget

- **GIVEN** `PROJECT_MOE_GUI_MODE_CLI_TIMEOUT_SECONDS` is set to `45`
- **WHEN** the shared toolchain invokes the target Mode CLI for a read-contract command
- **THEN** the subprocess timeout SHALL be `45.0` seconds

#### Scenario: Missing environment override uses full-suite headroom

- **GIVEN** no timeout override is set
- **WHEN** the shared toolchain invokes the target Mode CLI
- **THEN** the subprocess timeout SHALL be at least `45.0` seconds and default to the bounded repository value

#### Scenario: Invalid environment override falls back to default

- **GIVEN** the timeout override is empty, non-numeric, zero, or negative
- **WHEN** Project MOE GUI calculates the Mode CLI timeout budget
- **THEN** it SHALL ignore the invalid override and use the bounded default budget

### Requirement: GUI write and readback calls SHALL share the same timeout budget

Project MOE GUI write actions and their follow-up readback calls SHALL use the same Mode CLI timeout budget calculation so a loaded host does not pass one path and fail another solely because of inconsistent timeout constants.

#### Scenario: Write action and readbacks use one explicit budget

- **GIVEN** `PROJECT_MOE_GUI_MODE_CLI_TIMEOUT_SECONDS` is set to `45`
- **WHEN** a GUI write action performs the write command and required readback commands
- **THEN** every subprocess invocation in that write/readback sequence SHALL use timeout `45.0`

#### Scenario: Write action and readbacks use the default bounded budget

- **GIVEN** no timeout override is set
- **WHEN** a GUI write action performs the write command and required readback commands
- **THEN** every subprocess invocation in that write/readback sequence SHALL use the bounded 60 second default budget

#### Scenario: Configured budget remains fail-closed

- **GIVEN** a Mode CLI process exceeds the configured timeout budget
- **WHEN** the subprocess timeout expires
- **THEN** the existing timeout failure token `blocked:mode_cli_timeout` SHALL remain the failure classification
