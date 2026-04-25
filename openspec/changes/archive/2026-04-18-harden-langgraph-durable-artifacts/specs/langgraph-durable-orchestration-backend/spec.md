## MODIFIED Requirements

### Requirement: Research-to-implementation handoff SHALL persist a frozen implementation brief

The LangGraph durable flow SHALL persist research output as a stable frozen implementation brief before implementation begins from a fresh execution context.

The frozen brief SHALL be treated as a first-class durable artifact rather than as an informal planning note.

At minimum the persisted brief SHALL include:

- `brief_id`
- `thread_id`
- `objective`
- `non_goals`
- `accepted_decisions`
- `constraints`
- `interfaces`
- `ownership_boundaries`
- `acceptance_criteria`
- `validation_plan`
- `source_evidence_refs`
- `frozen_at`

Implementation execution SHALL restart from that frozen brief rather than from the full open-ended research context.

#### Scenario: Approved research is frozen for durable implementation

- **WHEN** research and planning have reached an approved handoff point
- **THEN** the workflow SHALL persist a frozen implementation brief as a durable artifact
- **AND** later implementation steps SHALL use that artifact as the handoff source
- **AND** the implementation lane SHALL begin in a fresh execution context rather than reusing the full research context

### Requirement: Adversarial bug review SHALL persist a survivor queue rather than a persistent bug triad

The LangGraph durable flow SHALL persist the judge-approved survivor queue as a stable durable artifact for downstream repair and verification work.

The workflow SHALL keep `bug-finder`, `bug-rebutter`, and `bug-judge` bursty by default.

At minimum each persisted survivor item SHALL include:

- `bug_id`
- `title`
- `severity`
- `evidence`
- `judge_verdict`
- `owner_lane`
- `status`
- `verification_result`
- `updated_at`

#### Scenario: Judge-approved survivors are handed to a durable repair lane

- **WHEN** adversarial review produces judged survivor items
- **THEN** the workflow SHALL persist only those survivor items as the durable repair queue
- **AND** it SHALL not require the review triad itself to remain default persistent workers
- **AND** a later repair or debugger lane SHALL be able to resume from the persisted queue

### Requirement: The LangGraph backend SHALL project inspectable thread state into the canonical durable-state surface

The LangGraph durable orchestration backend SHALL project repo-local thread state into the canonical inspectable durable-state surface.

At minimum the LangGraph projection SHALL make operator-facing state available for:

- stable thread identity
- current root-graph phase
- backend-record path
- interrupt or resume status
- checkpoint availability
- implementation-brief presence
- survivor-queue presence
- survivor-queue status or count when known
- inspect and resume pointers for durable artifacts when present

#### Scenario: Operator inspects a tracked LangGraph durable thread

- **WHEN** the current repository has a tracked LangGraph durable thread
- **THEN** the backend SHALL expose the data needed to populate the canonical inspectable durable-state summary
- **AND** it SHALL include LangGraph-specific projection fields for thread, phase, artifact presence, and resume-related state
