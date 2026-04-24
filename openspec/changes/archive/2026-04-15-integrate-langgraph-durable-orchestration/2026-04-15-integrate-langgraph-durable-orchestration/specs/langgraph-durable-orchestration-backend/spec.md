## ADDED Requirements

### Requirement: The repository SHALL provide an additive LangGraph durable orchestration backend
The repository SHALL provide a LangGraph-based durable orchestration backend that integrates under the existing Codex / oh-my-codex leader workflow rather than replacing it.

The backend SHALL preserve:

- the current main Codex CLI session as leader
- oh-my-codex as the user-level control and workflow layer
- LangGraph as the persistent orchestration kernel for selected long-running tasks

#### Scenario: Operator selects the LangGraph backend
- **WHEN** the operator enables the LangGraph durable orchestration backend
- **THEN** the workflow SHALL keep the current main Codex CLI session as leader
- **AND** it SHALL not redefine LangGraph as a replacement for Codex itself

### Requirement: The LangGraph backend SHALL persist repo-local threads and checkpoints
The LangGraph backend SHALL persist execution through repo-local thread identity and checkpoints.

At minimum:

- each durable execution SHALL use a stable `thread_id`
- `thread_id` SHALL include repository and worktree identity plus a task identifier
- checkpoint data SHALL remain discoverable from repo-local `.omx` state

#### Scenario: A long-running task is resumed
- **WHEN** the operator resumes a previously started LangGraph-orchestrated task
- **THEN** the backend SHALL locate the existing thread by stable repo-local identity
- **AND** it SHALL resume from persisted checkpoint state rather than restarting from scratch

### Requirement: The LangGraph backend SHALL mirror the seven-phase development flow in a root graph
The LangGraph backend SHALL provide a root graph that mirrors the durable team workflow phases:

- define-target
- read-context
- freeze-plan
- execute-parallel
- integrate-converge
- stabilize
- verify-accept

#### Scenario: Graph state advances from planning to execution
- **WHEN** the task has a frozen plan and enough execution slices to justify durable execution
- **THEN** the root graph SHALL be able to transition from `freeze-plan` into `execute-parallel`
- **AND** it SHALL preserve the current phase in persisted graph state

### Requirement: Research-to-implementation handoff SHALL persist a frozen implementation brief
The LangGraph durable flow SHALL persist research output as a frozen implementation brief instead of continuing implementation from the full open-ended research context.

That brief SHALL include structured fields covering at least:

- objective
- non-goals
- accepted decisions
- constraints
- ownership boundaries
- acceptance criteria

Execution SHALL restart from a fresh implementation context after the brief is frozen.

#### Scenario: Open-ended research moves into implementation
- **WHEN** research and planning have produced an approved implementation brief
- **THEN** the workflow SHALL persist that brief before durable execution begins
- **AND** the implementation path SHALL start from a fresh execution context rather than reusing the full research context

### Requirement: Adversarial bug review SHALL persist a survivor queue rather than a persistent bug triad
The LangGraph durable flow SHALL keep `bug-finder`, `bug-rebutter`, and `bug-judge` as bursty review roles.

What persists SHALL be the judge-approved survivor queue, including ownership and verification state for downstream repair work.

#### Scenario: Contested bug review feeds a debugger lane
- **WHEN** adversarial bug review produces judge-approved survivors
- **THEN** the workflow SHALL persist those survivors as a repair queue
- **AND** it SHALL not require `bug-finder`, `bug-rebutter`, and `bug-judge` to remain default persistent workers

### Requirement: The LangGraph backend SHALL support interrupts and operator-driven resume
The durable orchestration backend SHALL support human approval points that interrupt execution and later resume it from persisted state.

At minimum the first rollout SHALL support interruptable approval points around:

- plan freeze
- risky stabilization decisions
- failed final verification

#### Scenario: Plan-freeze approval pauses the graph
- **WHEN** the workflow reaches a plan-freeze approval point
- **THEN** the graph SHALL be able to interrupt and expose the pending state to the operator
- **AND** the operator SHALL be able to resume the same thread after approval
