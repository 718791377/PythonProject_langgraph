## MODIFIED Requirements

### Requirement: Expert timeout SHALL NOT be accepted as verification evidence

The orchestration activation policy SHALL require final reports to separate returned expert evidence from timed-out, stalled, abandoned, or main-session-taken-over verification.

The repository SHALL provide an executable expert lifecycle/wait/pacing evidence checker that can inspect saved run-summary or transcript evidence for completed-expert closure, preserved-thread exceptions, bounded wait windows, liveness/stall actions, and provider backpressure labels.

#### Scenario: A key-path expert times out

- **WHEN** a key-path expert or subagent times out or stalls
- **THEN** the session SHALL not use that lane as evidence
- **AND** it SHALL continue bounded wait, respawn a narrower expert, hand off to an eligible durable lane, or explicitly record main-session takeover

#### Scenario: Saved lifecycle evidence is checked

- **WHEN** saved expert lifecycle or wait evidence is passed to the expert lifecycle/wait/pacing evidence checker
- **THEN** the checker SHALL fail completed expert claims that omit closure evidence or a preserved-thread reason
- **AND** it SHALL fail wait claims that omit bounded wait windows or a total wait bound
- **AND** it SHALL fail liveness or stall claims that omit inspect, redirect, respawn, durable-handoff, or main-session-takeover action
- **AND** it SHALL fail provider pacing claims that treat upstream pacing as a reason to disable orchestration instead of labeled backpressure

### Requirement: Agent, skill, profile, and follow-up surfaces SHALL stay distinct

The orchestration activation policy SHALL keep native Codex subagents, workflow skills, plugin-provided skills, profile helpers, durable workers, and LangGraph nodes as distinct execution surfaces. Skills SHALL load from `SKILL.md` files and skills are not native subagents. Profile hard-load or soft-load SHALL NOT by itself start durable workers or satisfy persistent-team thresholds. Follow-up work after a completed and absorbed expert SHALL spawn a fresh agent unless the user explicitly asks to preserve the thread or a plan records a preserved-thread reason.

Standalone native-agent TOMLs SHALL remain separately checker-backed: present user-level and repo-local agent TOMLs SHALL pass `tools/check_custom_agent_toml_schema.py` by defining non-empty top-level `name`, `description`, and `developer_instructions` fields. Completed expert lifecycle evidence SHALL be checker-backed by `tools/check_expert_lifecycle_wait_pacing_evidence.py`, which requires completed experts to be closed after absorption unless a preserved-thread reason is explicit.

#### Scenario: A skill is invoked during an activation flow
- **WHEN** a workflow skill or plugin profile is used
- **THEN** the final evidence label SHALL NOT treat that invocation as a returned native expert result
- **AND** any later expert follow-up SHALL use a fresh agent unless preservation is explicit

#### Scenario: Native-agent TOML schema is checked
- **WHEN** the activation policy guard runs custom agent TOML schema validation
- **THEN** native-agent TOML validity SHALL be evaluated separately from skill `SKILL.md` validity
- **AND** missing or empty `name`, `description`, or `developer_instructions` fields SHALL fail the checker for any present standalone agent TOML

#### Scenario: Completed expert evidence requires closure or preservation
- **WHEN** a run summary says an expert returned and was absorbed
- **THEN** the saved evidence SHALL also show completed-agent closure or an explicit preserved-thread reason
- **AND** a later follow-up SHALL spawn a fresh agent unless preservation is explicit

### Requirement: Delegation SHALL preserve critical-path leader work
Delegation SHALL be concrete, bounded, self-contained, and materially advancing. The leader SHALL identify immediate critical-path work before delegating, SHALL NOT delegate urgent blocking work when the next leader action depends on the result, SHALL avoid duplicate leader/expert or expert/expert work, SHALL continue meaningful non-overlapping leader work while delegated work runs, and SHALL use `wait_agent` sparingly.

`wait_agent` use SHALL remain bounded with visible wait windows, liveness/progress checks, stall actions, and upstream provider pacing labels. Provider upstream pacing SHALL be reported as backpressure and SHALL NOT be used as a reason to disable LangGraph, OMX durable execution, or native subagents.

#### Scenario: A sidecar expert is running
- **WHEN** delegated sidecar work is in progress
- **THEN** the leader SHALL continue non-overlapping local work or record why it is blocked
- **AND** it SHALL not claim the delegated result as accepted without review and evidence labeling

#### Scenario: Wait and pacing evidence is checked
- **WHEN** saved evidence mentions `wait_agent`, liveness checks, stalled experts, or provider pacing
- **THEN** the expert lifecycle/wait/pacing checker SHALL require bounded wait windows and total bound evidence
- **AND** it SHALL require liveness/stall handling such as inspect, redirect, respawn, durable handoff, or main-session takeover
- **AND** it SHALL reject provider pacing language that disables orchestration rather than labeling backpressure
