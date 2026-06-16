## ADDED Requirements

### Requirement: Lifecycle Governance Maintains Durable-Team Proof Surfaces

Lifecycle governance SHALL register and preserve the durable-team delivery matrix, source traceability index, and process-group contract as first-class lifecycle proof surfaces. The lifecycle stack SHALL use these proof surfaces when source-backed durable-team refreshes affect white papers, research notes, North Star plans, lifecycle maps, implementation plans, playbooks, or OpenSpec specs.

The process-group contract SHALL be the handoff authority for deciding when a lifecycle layer, delivery gate, or release slice needs Inputs, Tools and Techniques, and Outputs. The source traceability index SHALL be the handoff authority for current source-run identity and tracked-versus-ignored evidence boundaries.

#### Scenario: Lifecycle refresh changes execution-facing guidance

- **GIVEN** a lifecycle refresh uses Business Management or PMP evidence and changes execution-facing durable-team guidance
- **WHEN** a maintainer checks whether the refresh is governed
- **THEN** the registry exposes the three proof-surface document pairs
- **AND** the lifecycle spec requires the source traceability index to identify the current fresh-reading run
- **AND** the lifecycle spec requires the process-group contract before execution-facing rules are treated as complete
- **AND** the lifecycle spec keeps raw extraction text and local cache logs outside tracked authority
