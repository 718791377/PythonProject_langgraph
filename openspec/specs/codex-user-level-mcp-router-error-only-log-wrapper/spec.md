# codex-user-level-mcp-router-error-only-log-wrapper Specification

## Purpose

Define an opt-in repository-local wrapper for running MCP Router bridge commands with error-only visible logs while preserving protocol output and retaining full raw diagnostics.

## Requirements

### Requirement: MCP Router log wrapper SHALL preserve protocol output while suppressing benign noise

The repository SHALL provide an opt-in wrapper for MCP Router bridge execution that preserves protocol-like stdout and suppresses known benign non-protocol noise from the main Codex session.

The wrapper SHALL:

- forward JSON-RPC-like stdout without modification
- suppress known benign non-protocol lines from stdout and stderr
- write every raw stdout and stderr line to a timestamped local log file
- forward actionable error lines to stderr
- report non-zero child process exit codes to stderr

#### Scenario: Benign MCP Router lifecycle noise appears during a normal run

- **WHEN** the wrapped child command emits benign updater, workflow fallback, PNG, or process-cleanup lines
- **THEN** those lines SHALL be written to the log file
- **AND** they SHALL NOT be shown in the main session
- **AND** normal protocol-looking stdout SHALL still be forwarded

#### Scenario: The child command emits an actionable error

- **WHEN** the wrapped child command emits a line matching an actionable error pattern
- **THEN** that line SHALL be written to the log file
- **AND** that line SHALL be forwarded to stderr

#### Scenario: The child command exits with a non-zero exit code

- **WHEN** the wrapped child command exits with a non-zero exit code
- **THEN** the wrapper SHALL return the same exit code
- **AND** it SHALL write a short error line to stderr that includes the log file path

### Requirement: MCP Router log wrapper SHALL NOT mutate user-level configuration

The repository implementation SHALL NOT edit user-level Codex configuration, MCP Router database state, or token storage while adding the wrapper.

`C:\Users\lenovo\.codex\config.toml` is the user-level Codex configuration file; repository scripts SHALL leave it operator-controlled.

#### Scenario: The wrapper is added to the repository

- **WHEN** the repository change is applied
- **THEN** `C:\Users\lenovo\.codex\config.toml` SHALL remain unchanged by repository scripts
- **AND** MCP Router database state SHALL remain unchanged by repository scripts
- **AND** operator documentation SHALL describe the wrapper as opt-in
