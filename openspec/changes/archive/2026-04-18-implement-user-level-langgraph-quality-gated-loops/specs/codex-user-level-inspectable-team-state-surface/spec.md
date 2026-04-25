## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project LangGraph loop progress explicitly

When the current repository has a tracked LangGraph durable thread inside a quality-gated loop, the canonical inspectable durable-state surface SHALL expose LangGraph-specific loop projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- `active_loop`
- `iteration_count`
- `iteration_budget`
- `last_gate_verdict`
- `last_gate_reason`
- `stop_reason`

#### Scenario: Operator inspects a looping LangGraph thread

- **WHEN** the current repository has a tracked LangGraph thread inside a quality-gated loop
- **THEN** the canonical summary SHALL expose the shared durable-state fields
- **AND** it SHALL include LangGraph loop-progress and gate-result projection data for operator inspection
