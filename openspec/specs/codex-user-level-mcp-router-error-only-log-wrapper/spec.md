# codex-user-level-mcp-router-error-only-log-wrapper Specification

## Purpose

Define an opt-in repository-local wrapper for running MCP Router bridge commands with error-only visible diagnostics while preserving MCP protocol bytes and retaining full raw logs.

## Requirements

### Requirement: MCP Router log wrapper SHALL preserve protocol output while suppressing benign noise

The repository SHALL provide an opt-in wrapper for MCP Router bridge execution.

The wrapper SHALL preserve child stdout byte-for-byte because stdout is the MCP protocol channel.

The wrapper SHALL copy wrapper stdin to child stdin byte-for-byte because stdin carries MCP protocol requests.

The wrapper SHALL filter visible child stderr by forwarding actionable error lines and writing benign stderr noise only to the local log file.

The wrapper SHALL write raw stdout and stderr chunks to a timestamped local log file.

The wrapper SHALL report non-zero child process exit codes to stderr and return the same exit code.

#### Scenario: JSON-RPC stdout has no trailing newline

- **WHEN** the wrapped child command emits JSON-RPC stdout without a trailing newline
- **THEN** the wrapper SHALL forward the exact stdout bytes without appending a newline

#### Scenario: Content-Length framed stdout is emitted

- **WHEN** the wrapped child command emits `Content-Length` framed stdout
- **THEN** the wrapper SHALL forward the exact stdout bytes without rewriting headers or body bytes

#### Scenario: Large tools/list stdout is emitted

- **WHEN** the wrapped child command emits a large `tools/list`-like JSON-RPC response
- **THEN** the wrapper SHALL forward the complete stdout payload unchanged

#### Scenario: Benign MCP Router diagnostic noise appears on stderr

- **WHEN** the wrapped child command emits benign updater, workflow fallback, PNG, or process-cleanup lines on stderr
- **THEN** those lines SHALL be written to the log file
- **AND** they SHALL NOT be shown in the main session

#### Scenario: The child command emits an actionable stderr error

- **WHEN** the wrapped child command emits a line matching an actionable error pattern on stderr
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
