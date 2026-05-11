## ADDED Requirements

### Requirement: Automatic team routing SHALL keep selector source and compatibility records separate

Automatic durable-team routing SHALL treat `.omx/state/selectors/active.json` as the authority for automatic adoption of existing durable state.

Compatibility records such as `.omx/state/langgraph/backend.json` and `.omx/state/team/codex-auto-managed-team.json` MAY be used as inspection context, but SHALL NOT alone authorize adopting unmanaged or unscoped existing teams or threads.

#### Scenario: Active selector is missing while LangGraph is ready

- **WHEN** LangGraph is the default ready durable backend but `.omx/state/selectors/active.json` is missing
- **THEN** status output SHALL report a selector refresh gap
- **AND** it SHALL NOT downgrade the backend to unavailable
- **AND** it SHALL NOT auto-adopt unmanaged compatibility records as active selectors
