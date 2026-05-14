## MODIFIED Requirements

### Requirement: The main Codex CLI session SHALL remain the leader

The current main Codex CLI session SHALL remain the leader for activation checks, role selection, worker briefs, fan-in, evidence labeling, final integration, and release recommendations. Orchestration SHALL NOT require a separate persistent leader pane, and workers, skills, plugin profiles, and LangGraph nodes SHALL NOT become independent release authorities. Adoption decisions SHALL be scoped to the current task flow rather than whether the repository is newly created.

Main-session leader and task-flow scope evidence SHALL be script-checkable. The repository SHALL provide `tools/check_leader_session_scope_evidence.py` to validate saved evidence for leader-owned fan-in, evidence labeling, final integration or release recommendations, no separate persistent leader pane replacement, startup non-autolaunch with durable-team threshold evidence, task-flow scoped adoption, and legacy resumed sessions that remain compatibility-scoped under current repository governance and capability-chain policy.

#### Scenario: Existing project resumes work

- **WHEN** an existing project or legacy resumed session continues a task flow
- **THEN** the main session SHALL apply current repository governance and capability-chain policy
- **AND** it SHALL keep local mainline and publication decisions under user-authorized leader control
- **AND** saved leader/session scope evidence SHALL pass `tools/check_leader_session_scope_evidence.py`

#### Scenario: Startup or first activation does not auto-launch a durable team

- **WHEN** startup or first activation evidence reports no durable team
- **THEN** it SHALL cite a concrete unmet threshold such as `threshold_not_met:no_frozen_plan` or `threshold_not_met:single_execution_slice`
- **AND** it SHALL NOT claim that Codex startup itself auto-launches a durable team

#### Scenario: Routing adoption is task-flow scoped

- **WHEN** orchestration adoption is decided for an existing project or a new repository
- **THEN** the decision SHALL cite current task-flow phase, thresholds, blockers, or task-fit evidence
- **AND** it SHALL NOT use repository age or new/existing project status as the adoption basis
