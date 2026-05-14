## MODIFIED Requirements

### Requirement: Exploration, code-change delegation, and durable artifact persistence SHALL stay script-checkable

Read-only exploration SHALL be used for specific codebase questions, symbol mapping, or file discovery. It SHALL NOT replace a bounded code-changing worker task when a safe implementation patch is clear. LangGraph entrypoints and repo-local `.omx/state/langgraph/` state SHALL be used when graph phases, checkpoint gates, frozen briefs, survivor queues, or tracked LangGraph thread state are required. `.omx/state/selectors/active.json` SHALL remain the active selector authority for automatic durable-team adoption; compatibility records SHALL be context only. Durable artifacts, frozen briefs, and survivor queues SHALL be written to repo-local state or documented artifact paths rather than only transient chat context. The repository SHALL provide `tools/check_durable_artifact_state_surfaces.py` to validate repository policy surfaces and saved run-summary, worker-brief, or durable handoff evidence for these boundaries.

#### Scenario: Graph-shaped checkpoint work is selected

- **WHEN** the task requires checkpoint gates, frozen briefs, survivor queues, or tracked LangGraph thread state
- **THEN** the durable workflow SHALL use LangGraph entrypoints and repo-local `.omx/state/langgraph/` state
- **AND** the durable artifacts SHALL have documented artifact paths or repo-local state locations
- **AND** automatic durable-team adoption SHALL cite `.omx/state/selectors/active.json` rather than compatibility records alone

#### Scenario: Exploration does not replace bounded implementation

- **GIVEN** the implementation patch is clear and safe to delegate
- **WHEN** read-only exploration evidence is recorded
- **THEN** exploration SHALL remain specific, well-scoped, and read-only
- **AND** it SHALL NOT be the only evidence surface for the code-changing implementation task

#### Scenario: Durable handoff artifacts are persisted

- **WHEN** research fan-in creates a frozen implementation brief or adversarial review leaves survivor candidates
- **THEN** the brief or survivor queue SHALL be persisted to repo-local state or documented artifact paths
- **AND** it SHALL include the required handoff fields or debugger-lane follow-up evidence instead of existing only in transient chat context
