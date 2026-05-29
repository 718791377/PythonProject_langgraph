## ADDED Requirements

### Requirement: Governance plan SHALL use the executable modern Comet structure

The user-level MCP, skills, browser automation, and CLI harness governance plan SHALL include worker-facing Goal, Architecture, and Tech Stack opening blocks plus execution-oriented sections for file ownership, readiness, task backlog, acceptance, evidence, rollback, and risks.

#### Scenario: Modern sections are present

- **WHEN** the plan is reviewed manually
- **THEN** it SHALL include Goal, Architecture, Tech Stack, file responsibility map, definition of ready, task-level backlog, acceptance criteria, required evidence, rollback, and risks
- **AND** it SHALL preserve Token/risk priority, authorization receipt, update receipt, evidence redaction, port registry/lease, codex-port allocator, pending_bind, registry_revision, 39000-39299, 40000-40999, OpenSpec slice, and fail closed governance markers

#### Scenario: Runtime lanes remain risk-gated

- **WHEN** a lane lacks install, smoke, receipt, or rollback evidence
- **THEN** it SHALL stay below active
- **AND** sensitive MCP, browser, CDP Bridge, OpenCLI, CLI-Anything, and WeCom actions SHALL require current authorization receipt evidence
