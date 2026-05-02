## MODIFIED Requirements

### Requirement: MCP Router log wrapper SHALL preserve protocol output while suppressing benign noise

The wrapper SHALL preserve child stdout byte-for-byte because stdout is the MCP protocol channel.

The wrapper SHALL filter visible child stderr by forwarding actionable error lines and writing benign stderr noise only to the local log file.

#### Scenario: JSON-RPC stdout has no trailing newline

- **WHEN** the wrapped child command emits JSON-RPC stdout without a trailing newline
- **THEN** the wrapper SHALL forward the exact stdout bytes without appending a newline

#### Scenario: Content-Length framed stdout is emitted

- **WHEN** the wrapped child command emits `Content-Length` framed stdout
- **THEN** the wrapper SHALL forward the exact stdout bytes without rewriting headers or body bytes

#### Scenario: Large tools/list stdout is emitted

- **WHEN** the wrapped child command emits a large `tools/list`-like JSON-RPC response
- **THEN** the wrapper SHALL forward the complete stdout payload unchanged
