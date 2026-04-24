## ADDED Requirements

### Requirement: Reusable subgraph contracts SHALL declare command-aware parent-exit boundaries

Reusable subgraph contracts SHALL declare command-aware parent-exit boundaries when a subgraph is allowed to hand control back to the parent graph.

At minimum that contract SHALL be able to describe:

- source subgraph identity
- allowed parent-target scope
- expected handoff artifacts or state updates

#### Scenario: Planning subgraph exits through a parent-directed handoff

- **WHEN** the reusable `planning` subgraph is allowed to hand control back to the parent graph
- **THEN** the contract SHALL declare that parent-exit boundary explicitly
- **AND** it SHALL not leave the handoff as an undocumented implicit transition

### Requirement: Reusable subgraph contracts SHALL preserve explicit handoff boundaries for command-driven continuation

When a reusable subgraph participates in command-driven continuation, the contract SHALL preserve explicit handoff boundaries instead of implying unrestricted cross-subgraph routing.

#### Scenario: Research hands off with explicit command-driven continuation into planning

- **WHEN** the durable workflow transitions from the reusable `research` subgraph into the reusable `planning` subgraph through command-driven continuation
- **THEN** the contract SHALL preserve the explicit handoff boundary and expected handoff artifact posture
- **AND** it SHALL not imply unrestricted full-context carryover by default
