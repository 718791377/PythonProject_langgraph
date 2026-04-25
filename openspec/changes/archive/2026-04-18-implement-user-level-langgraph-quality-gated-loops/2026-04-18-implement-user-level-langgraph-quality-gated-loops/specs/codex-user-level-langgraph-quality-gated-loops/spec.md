## ADDED Requirements

### Requirement: The user-level LangGraph lane SHALL support graph-native conditional routing

The user-level LangGraph lane SHALL route execution inside the graph by node-produced gate verdicts rather than treating LangGraph only as a persisted wrapper around one-pass phase transitions.

#### Scenario: Gate verdict selects the next node

- **WHEN** a LangGraph gate node returns `revise`
- **THEN** the graph SHALL follow the revise edge for that loop family
- **AND** it SHALL not mark the current flow accepted or complete

### Requirement: The user-level LangGraph lane SHALL support bounded quality-gated loops

The user-level LangGraph lane SHALL support bounded iterative loops for selected quality-sensitive flows.

At minimum the first rollout SHALL support:

- `draft -> review -> revise -> review -> accept`
- `execute -> verify -> revise -> execute`

#### Scenario: Verification failure triggers another execution iteration

- **WHEN** verification returns a non-accepting verdict that remains repairable
- **THEN** the graph SHALL loop back into the execution path
- **AND** it SHALL persist the new iteration count

### Requirement: Quality-gated loops SHALL terminate explicitly

Each quality-gated loop SHALL terminate by one explicit outcome:

- accepted
- escalated
- interrupted for human decision
- exhausted iteration budget
- halted by non-repairable failure

#### Scenario: Iteration budget is exhausted

- **WHEN** a loop reaches its configured iteration budget without acceptance
- **THEN** the thread SHALL stop with an explicit exhaustion state
- **AND** it SHALL expose that state through inspectable status output

### Requirement: Loop state SHALL be persisted and resumable

The LangGraph backend SHALL persist loop metadata as part of thread state so that interrupted or restarted execution can resume deterministically.

#### Scenario: Interrupted loop is resumed

- **WHEN** an interrupted LangGraph thread is resumed during an active quality loop
- **THEN** the backend SHALL restore the active loop name, iteration count, and last gate verdict
- **AND** it SHALL continue from the persisted checkpoint rather than restarting the loop from iteration one
