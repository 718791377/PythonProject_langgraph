## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose additive streaming and debug observability for tracked threads

The user-level LangGraph backend SHALL expose additive streaming and debug observability for tracked threads instead of limiting operator visibility to snapshot inspection only.

The first rollout SHALL support at minimum these operator-facing event modes:

- `updates`
- `checkpoints`
- `tasks`
- `debug`

#### Scenario: Operator streams task and checkpoint observability for a tracked thread

- **WHEN** the operator requests streaming observability for a tracked LangGraph thread
- **THEN** the backend SHALL expose the selected stream modes as additive observability behavior
- **AND** it SHALL not require the operator to replace existing snapshot inspection to use the stream surface

### Requirement: The LangGraph backend SHALL preserve nested subgraph visibility for stream observability

When streaming observability is enabled with nested subgraph visibility, the backend SHALL preserve that posture explicitly.

#### Scenario: Operator enables nested subgraph visibility for a streamed thread

- **WHEN** the operator requests stream observability with nested subgraph visibility
- **THEN** the backend SHALL preserve that posture in stream-session or equivalent bounded observability state
- **AND** it SHALL keep nested subgraph visibility distinguishable from root-only stream posture

### Requirement: The LangGraph backend SHALL project bounded latest-event stream posture for inspection

The backend SHALL project bounded latest-event stream posture for inspection without requiring a full persisted event log in the canonical durable-state summary.

At minimum that projection SHALL be able to report:

- selected stream modes
- whether nested subgraphs are included
- latest event kind
- latest checkpoint or task signal when present

#### Scenario: Operator inspects the latest bounded stream posture after a streamed execution step

- **WHEN** a tracked LangGraph thread has emitted streamed observability events
- **THEN** the backend SHALL preserve a bounded latest-event stream posture for later inspection
- **AND** it SHALL not overstate that bounded summary as a full stream-history replacement
