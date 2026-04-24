## ADDED Requirements

### Requirement: Session-scoped durable activation SHALL be separated from legacy durable artifacts
The user-level durable orchestration layer SHALL separate future-session activation state from legacy repo-local durable artifact state.

Legacy durable artifact files under `.omx/state/langgraph/*` and `.omx/state/team/*` SHALL remain readable and inspectable, but they SHALL NOT by themselves act as the authoritative activation selector for unrelated future sessions.

#### Scenario: Preserved legacy LangGraph backend record exists without scoped activation
- **WHEN** a repository contains a preserved legacy LangGraph backend record with a `thread_id`
- **AND** no scoped activation selector or lease declares that record active for the current future session
- **THEN** the durable orchestration layer SHALL preserve that record as inspectable legacy artifact state
- **AND** it SHALL NOT treat that record alone as the active future-session durable selector

### Requirement: New durable activation writes SHALL use a scoped selector or lease plane
New durable activation writes SHALL use a scoped selector or lease plane instead of writing future-session activation truth only into legacy artifact summaries.

That scoped activation plane SHALL identify at minimum:

- backend family
- repo root
- worktree identity
- session scope or session lineage
- activation generation or equivalent freshness signal

#### Scenario: New future session acquires LangGraph durable activation
- **WHEN** a future session activates LangGraph durable orchestration for a task flow
- **THEN** the user-level layer SHALL write activation truth into a scoped selector or lease plane
- **AND** it SHALL NOT rely only on legacy `backend.json` presence as the source of that activation truth

### Requirement: Scoped activation failure SHALL fail closed
If the user-level durable orchestration layer cannot safely determine a scoped activation target, it SHALL fail closed for new activation writes rather than silently falling back to legacy implicit activation.

#### Scenario: Scoped activation target cannot be derived safely
- **WHEN** the runtime cannot determine a safe scoped activation target for a new durable decision
- **THEN** it SHALL refuse to treat legacy artifact presence alone as the activation source
- **AND** it SHALL surface an explicit safe non-mutating result or blocker instead of silently activating the legacy record
