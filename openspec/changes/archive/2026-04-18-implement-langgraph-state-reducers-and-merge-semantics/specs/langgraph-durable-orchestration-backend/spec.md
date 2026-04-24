## ADDED Requirements

### Requirement: The user-level LangGraph lane SHALL define explicit reducer-backed merge channels for fan-out and fan-in state

The user-level LangGraph durable lane SHALL define explicit reducer-backed state channels for branch outputs that are intended to merge across parallel fan-out and fan-in execution.

The contract SHALL distinguish reducer-merged channels from single-writer channels.

The system SHALL NOT silently treat arbitrary multi-writer state updates as mergeable.

#### Scenario: Parallel execution branches return mergeable findings

- **WHEN** multiple LangGraph execution branches complete with outputs for a declared reducer-merged channel
- **THEN** the durable lane SHALL merge those outputs through the declared reducer semantics
- **AND** it SHALL persist the merged result in repo-local LangGraph durable state

#### Scenario: Multiple branches write to a non-reducer field

- **WHEN** multiple LangGraph branches attempt to write the same field that is not declared as reducer-merged
- **THEN** the durable lane SHALL reject or surface that write as invalid multi-writer state
- **AND** it SHALL NOT silently resolve the conflict through implicit overwrite or append behavior

### Requirement: Reducer-backed fan-in state SHALL remain deterministic and resumable

Reducer-backed fan-in behavior SHALL be deterministic enough for checkpoint resume and equivalent branch-result reapplication to preserve the same durable state meaning.

Reducer-aware branch records SHALL therefore preserve stable item identity or equivalent dedup-safe semantics where append-like merging is used.

#### Scenario: Interrupted parallel flow resumes after partial branch completion

- **WHEN** a LangGraph thread resumes after some fan-out branches have already contributed reducer-backed results
- **THEN** the resumed flow SHALL preserve the already-merged branch contributions
- **AND** it SHALL continue fan-in without corrupting or duplicating the durable merged state

### Requirement: Leader-owned summary fields SHALL remain separate from reducer-merged branch channels

The durable lane SHALL keep leader-owned summary fields distinct from reducer-merged branch channels.

Fields that define top-level durable posture, identity, or accepted outcome SHALL remain single-writer unless explicitly reclassified by a later change.

#### Scenario: Branch fan-in completes before final leader convergence

- **WHEN** reducer-backed branch channels have been merged successfully
- **THEN** the durable lane MAY expose the merged branch state as intermediate durable state
- **AND** it SHALL NOT treat that merged branch state as the final accepted thread outcome until leader-owned convergence completes
