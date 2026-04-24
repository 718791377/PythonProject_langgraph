## ADDED Requirements

### Requirement: The user-level LangGraph lane SHALL expose a reusable subgraph library for persistent agent-team role families

The user-level LangGraph durable lane SHALL expose a reusable subgraph library for the persistent agent-team role families:

- `research`
- `planning`
- `execution`
- `verification`
- `adversarial-review`

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
