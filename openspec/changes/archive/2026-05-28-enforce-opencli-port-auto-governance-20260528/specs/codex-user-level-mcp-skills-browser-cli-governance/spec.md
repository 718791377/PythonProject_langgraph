## ADDED Requirements

### Requirement: OpenCLI governance guard SHALL require port auto and codex-port lease evidence

The repository-local OpenCLI governance guard SHALL fail closed unless OpenCLI pre-dispatch checks use allocator-driven `--port auto` and provide sanitized codex-port lease evidence for the Codex browser/OpenCLI range.

The guard SHALL treat hard-coded OpenCLI ports as unsafe, even when browser owner evidence and authorization receipts are otherwise valid.

#### Scenario: OpenCLI action lacks port lease evidence

- **WHEN** `python tools/opencli_governance.py check --action session.inspect --target tab:opencli-1 --session session-a --json` runs without a port lease receipt
- **THEN** the command SHALL fail closed
- **AND** it SHALL include `opencli_port_lease_receipt_required` in blockers
- **AND** it SHALL report `dispatch_allowed=false`

#### Scenario: OpenCLI action uses a hard-coded port

- **WHEN** the guard checks an action with `--port 39300`
- **THEN** the command SHALL fail closed
- **AND** it SHALL include `opencli_port_must_be_auto` in blockers
- **AND** it SHALL report hard-coded OpenCLI ports are not allowed

#### Scenario: OpenCLI port lease is outside the Codex OpenCLI range

- **WHEN** the guard receives a codex-port lease receipt whose port is outside `39300-39499`
- **THEN** the command SHALL fail closed
- **AND** it SHALL include `opencli_port_lease_range_mismatch` in blockers
