## ADDED Requirements

### Requirement: The user-level LangGraph lane SHALL expose read-oriented replay and state-history inspection for tracked threads

The user-level LangGraph durable lane SHALL expose read-oriented replay, checkpoint-history inspection, and state-history inspection for tracked LangGraph threads.

At minimum the inspection surface SHALL be able to identify:

- the tracked thread identity
- available checkpoint or history targets
- the phase or lifecycle posture associated with each target
- the persisted source records used to derive the replay or history view
- the follow-up helper pointers for resume or explicit recovery

#### Scenario: Operator inspects checkpoint history for a tracked LangGraph thread

- **WHEN** the current repository has a tracked LangGraph durable thread with persisted checkpoint or state-history records
- **THEN** the durable lane SHALL expose those records through a read-oriented inspection surface
- **AND** it SHALL not mutate the tracked active thread state as part of that inspection

### Requirement: LangGraph replay SHALL remain distinct from recovery mutation

Replay or history inspection SHALL remain read-only by default.

The durable lane SHALL distinguish replaying or viewing prior state from mutating the tracked active thread state through recovery controls.

#### Scenario: Operator replays a prior checkpoint for analysis

- **WHEN** the operator requests replay or inspection of a prior LangGraph checkpoint
- **THEN** the durable lane SHALL expose the historical view or replay result as inspection output
- **AND** it SHALL not treat that replay action as an implicit rewind or state rewrite

### Requirement: LangGraph time-travel SHALL require an explicit recovery target

The user-level LangGraph durable lane SHALL support bounded time-travel only as an explicit recovery action against a stable checkpoint or state-history target.

#### Scenario: Operator time-travels a tracked LangGraph thread to a prior checkpoint

- **WHEN** the operator explicitly selects an eligible checkpoint or history target for recovery
- **THEN** the durable lane SHALL apply recovery against that explicit target
- **AND** it SHALL mark the resulting thread posture as recovered or equivalent rather than pretending no recovery occurred

### Requirement: Update-state-style recovery SHALL remain bounded and contract-preserving

The user-level LangGraph durable lane SHALL support explicit update-state-style recovery only within bounded recoverable-field classes that preserve the existing durable-state contract.

It SHALL NOT expose arbitrary raw state mutation as the default operator recovery path.

#### Scenario: Operator applies bounded state repair to a tracked LangGraph thread

- **WHEN** the operator requests explicit state repair for a recoverable LangGraph state field
- **THEN** the durable lane SHALL validate that the requested repair is in scope and contract-compatible
- **AND** it SHALL reject or surface out-of-scope, invalid, or reducer-breaking mutations explicitly

### Requirement: Replay and recovery SHALL preserve source attribution and recovery provenance

Replay and recovery surfaces SHALL preserve source attribution for the underlying state records and SHALL expose whether the current thread posture reflects historical replay, explicit recovery, or ordinary uninterrupted execution.

#### Scenario: Operator inspects a thread after time-travel recovery

- **WHEN** a tracked LangGraph thread has undergone explicit recovery
- **THEN** the durable lane SHALL expose source pointers and recovery provenance for the resulting thread posture
- **AND** it SHALL not collapse recovered state into an indistinguishable uninterrupted-active classification
