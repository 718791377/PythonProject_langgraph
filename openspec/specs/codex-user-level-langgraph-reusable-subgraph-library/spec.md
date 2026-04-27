# codex-user-level-langgraph-reusable-subgraph-library Specification

## Purpose

Define the reusable, inspectable LangGraph subgraph library for the user-level Codex persistent agent-team lane.

## Requirements

### Requirement: The user-level LangGraph lane SHALL expose a reusable subgraph library for persistent agent-team role families

The user-level LangGraph durable lane SHALL expose a reusable subgraph library for the persistent agent-team role families:

- `research` - reusable subgraph family for external or open-ended research work.
- `planning` - reusable subgraph family for plan freezing and slice preparation.
- `execution` - reusable subgraph family for implementation or worker execution.
- `verification` - reusable subgraph family for acceptance and evidence validation.
- `adversarial-review` - reusable subgraph family for bug-finder, rebutter, and judge review loops.

Each subgraph SHALL have a stable subgraph identity and SHALL remain additive under the existing Codex CLI leader model.

#### Scenario: Operator inspects the reusable subgraph library

- **WHEN** the operator inspects the user-level LangGraph subgraph library
- **THEN** the library SHALL expose the supported reusable subgraph identities
- **AND** it SHALL not present them as Codex-native always-on worker panes by default

### Requirement: Each reusable subgraph contract SHALL declare role family and handoff boundaries

Each reusable subgraph contract SHALL be richer than a role-name list.

At minimum it SHALL declare:

- subgraph identity
- role family
- supported roles
- expected input artifacts
- expected output artifacts
- whether a fresh-context boundary is required

#### Scenario: Research hands off into planning

- **WHEN** the durable workflow transitions from the reusable `research` subgraph into the reusable `planning` subgraph
- **THEN** the contract SHALL expose that research produces a frozen implementation brief
- **AND** it SHALL preserve the explicit handoff boundary instead of implying unrestricted context carryover

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
