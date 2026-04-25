## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project streaming posture for tracked LangGraph threads

When the current repository has a tracked LangGraph durable thread with active or recent stream observability posture, the canonical inspectable durable-state surface SHALL expose LangGraph-specific streaming posture data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- selected stream modes
- whether nested subgraphs are included
- latest event kind
- the relevant stream-observability helper pointer

#### Scenario: Operator inspects a tracked LangGraph thread after streaming debug observability

- **WHEN** the current repository has a tracked LangGraph thread with stream-observability posture
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include bounded streaming posture and helper-pointer projection data

### Requirement: The canonical durable-state surface SHALL keep latest-event stream summaries bounded

The inspectable durable-state surface SHALL keep latest-event streaming summaries bounded rather than projecting an unbounded raw event log through the canonical summary.

#### Scenario: Operator inspects a debug-heavy LangGraph thread

- **WHEN** the current repository has a tracked LangGraph thread that emitted multiple debug or task events
- **THEN** the canonical inspectable durable-state surface SHALL expose a bounded latest-event stream summary
- **AND** it SHALL not require the canonical summary to become a full raw stream transcript
