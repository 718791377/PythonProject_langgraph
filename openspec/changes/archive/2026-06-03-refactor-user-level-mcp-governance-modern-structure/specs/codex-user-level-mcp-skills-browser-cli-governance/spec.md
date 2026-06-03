## ADDED Requirements

### Requirement: Governance plan SHALL use the modern implementation-plan structure

The user-level MCP, skills, browser automation, and CLI harness governance plan SHALL present its implementation model with the same modern structure family used by the Pi sidecar and Comet runtime plans.

#### Scenario: Structure includes runtime and governance sections

- **WHEN** the plan is reviewed after this refactor
- **THEN** it SHALL include relationship boundaries, goals/non-goals, runtime architecture, Codex usage, repo-local source of truth, user-level artifacts and receipts, state contract, phase gates, implementation slices, task backlog, local integration order, acceptance criteria, evidence, rollback, and risks
- **AND** it SHALL preserve `skills2cli`, `mcp2cli`, `chrome-devtools-mcp`, CDP Bridge, OpenCLI, CLI-Anything, `wecom-cli`, port registry, `codex-port`, `pending_bind`, `registry_revision`, `39000-39299`, `40000-40999`, authorization receipt, update receipt, and evidence-redaction governance markers

#### Scenario: Runtime actions remain gated

- **WHEN** a lane is still missing wrapper, smoke, receipt, or rollback evidence
- **THEN** the plan SHALL keep that lane below `active`
- **AND** it SHALL require explicit current authorization receipts for sensitive MCP/browser/CDP/OpenCLI/WXWork actions
