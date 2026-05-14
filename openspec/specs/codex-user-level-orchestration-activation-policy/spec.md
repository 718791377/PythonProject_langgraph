# Codex User-Level Orchestration Activation Policy

## Purpose

Define the reusable user-level orchestration-activation policy for Codex CLI so orchestration can be re-checked, retrofitted, and actually adopted across new and existing task flows.
## Requirements
### Requirement: The user-level installation SHALL expose an orchestration-activation policy

The user-level installation SHALL expose a reusable orchestration-activation policy for Codex CLI.

That policy SHALL define:

- that activation is scoped to the current task flow
- that activation is not limited to new projects or new sessions
- which events require activation re-checks
- what counts as a hard routing directive
- what Codex CLI must do when activation thresholds are met and no blocker exists

#### Scenario: Operator inspects the user-level activation policy

- **WHEN** the operator inspects the user-level orchestration policy surfaces
- **THEN** they SHALL be able to identify activation posture, re-check triggers, hard directives, and retrofit rules
- **AND** they SHALL not have to infer those rules only from repository-local project documents

### Requirement: Existing projects and existing sessions SHALL remain orchestration-retrofit capable

The user-level orchestration policy SHALL support retrofit for:

- existing projects with new sessions
- existing live sessions after reload, restart, explicit user routing directive, or tracked durable-state detection

#### Scenario: Existing live session is explicitly told to use `omx`

- **WHEN** the user explicitly tells Codex CLI to use `omx`
- **THEN** Codex CLI SHALL treat that instruction as a hard routing directive
- **AND** it SHALL adopt the orchestration path unless a concrete blocker exists
- **AND** if it does not adopt the orchestration path, it SHALL explain the concrete blocker

### Requirement: Activation traces SHALL expose full orchestration state
The user-level orchestration activation policy SHALL require activation traces to report task phase, capability-chain state, default durable backend, backend readiness, expert selection, durable workflow state, persistent-team state, and a concrete reason.

The trace vocabulary SHALL distinguish `not_needed`, `candidate`, `selected`, `blocked`, and `running`.

The repository SHALL provide an executable trace-evidence validator that can inspect saved activation trace text for required fields, capability-chain consistency, backend readiness semantics, durable workflow and persistent-team vocabulary, forbidden missing-reminder reasons, expert-timeout evidence labels, and durable-team threshold evidence in the `why` field. It SHALL also provide `tools/check_expert_lifecycle_wait_pacing_evidence.py` for saved run-summary evidence covering completed-expert closure, preserved-thread exceptions, bounded wait windows, liveness/stall actions, and provider pacing as backpressure.

#### Scenario: Saved trace evidence is checked
- **WHEN** a saved activation trace is passed to the repository trace-evidence validator
- **THEN** the validator SHALL fail if any required trace field is missing
- **AND** it SHALL fail if capability-chain dependency states are inconsistent
- **AND** it SHALL fail if durable workflow or persistent-team states use unsupported vocabulary
- **AND** it SHALL fail if expert timeout language is presented without a non-evidence, bounded-wait, respawn, durable-handoff, or main-session-takeover label
- **AND** it SHALL fail if durable workflow or persistent-team decisions omit required unmet-threshold, named-blocker, or triggered-threshold evidence from `why`

### Requirement: Missing user reminders SHALL NOT be a routing reason

The orchestration activation policy SHALL forbid using "the user did not request parallelism", "the user did not request subagents", or equivalent missing-reminder language as the reason for not using experts, durable workflow, or persistent team.

#### Scenario: A small single-file task does not need a durable team

- **WHEN** the current task is a small single-file task
- **THEN** the trace MAY report `persistent_team=not_needed`
- **AND** the reason SHALL cite task phase, scope, risk, or threshold state
- **AND** it SHALL NOT cite missing user instructions as the reason

### Requirement: Expert timeout SHALL NOT be accepted as verification evidence

The orchestration activation policy SHALL require final reports to separate returned expert evidence from timed-out, stalled, abandoned, or main-session-taken-over verification.

The repository SHALL provide an executable expert lifecycle/wait/pacing evidence checker that can inspect saved run-summary or transcript evidence for completed-expert closure, preserved-thread exceptions, bounded wait windows, liveness/stall actions, and provider backpressure labels.

#### Scenario: A key-path expert times out

- **WHEN** a key-path expert or subagent times out or stalls
- **THEN** the session SHALL not use that lane as evidence
- **AND** it SHALL continue bounded wait, respawn a narrower expert, hand off to an eligible durable lane, or explicitly record main-session takeover

#### Scenario: Saved expert lifecycle and wait evidence is checked

- **WHEN** saved expert lifecycle or wait evidence is passed to the expert lifecycle/wait/pacing evidence checker
- **THEN** the checker SHALL fail completed expert claims that omit closure evidence or a preserved-thread reason
- **AND** it SHALL fail wait claims that omit bounded wait windows or a total wait bound
- **AND** it SHALL fail liveness or stall claims that omit inspect, redirect, respawn, durable-handoff, or main-session-takeover action
- **AND** it SHALL fail provider pacing claims that treat upstream pacing as a reason to disable orchestration instead of labeled backpressure

### Requirement: Existing sessions SHALL retrofit activation policy at safe boundaries

Existing live sessions SHALL re-run activation checks after reload, restart, resume, continue, phase change, durable-state detection, capability-state change, or expert timeout.

#### Scenario: A legacy session is resumed

- **WHEN** a legacy resumed session continues work in this repository
- **THEN** it SHALL treat current repository governance and capability-chain policy as authoritative
- **AND** it SHALL not allow stale runtime assumptions to override current policy

### Requirement: First activation traces SHALL report durable-team threshold evidence
Startup and first activation traces SHALL include durable-team threshold evidence.

When a durable team is not selected, the trace SHALL cite the concrete unmet threshold, such as `threshold_not_met:no_frozen_plan`, `threshold_not_met:single_execution_slice`, or an equivalent phase/scope threshold. When a durable team is blocked, the trace SHALL cite a named blocker or unmet threshold. When a durable team is selected or running, the trace SHALL cite the concrete trigger, such as `triggered_threshold:frozen_plan_with_2+_independent_slices`, a frozen plan with two or more independent execution slices, or a stabilization phase with named blocking issues.

#### Scenario: First activation does not select a durable team
- **WHEN** a session emits its first activation trace for startup, resume, or continue
- **AND** durable-team thresholds are not met
- **THEN** the trace SHALL report `persistent_team=not_needed` or `persistent_team=blocked`
- **AND** the trace SHALL identify the unmet durable-team threshold or named blocker in `why`
- **AND** it SHALL NOT imply that missing user reminders caused the no-team decision

#### Scenario: First activation selects a durable team
- **WHEN** a session emits its first activation trace
- **AND** the plan is frozen with two or more independent execution slices or the stabilization threshold is met
- **THEN** the trace SHALL report the durable-team lane as `selected` or `running`
- **AND** the trace SHALL identify the concrete threshold trigger in `why`

#### Scenario: Trace validator rejects vague durable-team decisions
- **WHEN** saved trace evidence reports `persistent_team=not_needed` without `threshold_not_met:*` or equivalent unmet-threshold language in `why`
- **OR** it reports `persistent_team=blocked` without `blocked:*` or unmet-threshold language in `why`
- **OR** it reports `persistent_team=selected` or `persistent_team=running` without `triggered_threshold:*` or equivalent trigger language in `why`
- **THEN** the trace-evidence validator SHALL fail the trace

### Requirement: Hard routing directives SHALL require adoption or named blockers

The orchestration activation policy SHALL treat explicit requests for `omx` or `LangGraph` as hard routing directives for the current task flow.

When the capability chain, preflight, and task thresholds are satisfied, the session SHALL report the selected lane as `selected` or `running` and SHALL NOT remain in explanation-only mode. When the requested lane is not adopted, the trace SHALL report a named blocker or unmet threshold such as `blocked:backend_not_ready`, `blocked:preflight_failed`, `blocked:helper_missing`, `blocked:write_ownership_conflict`, or `threshold_not_met:no_frozen_plan`.

The repository SHALL provide `tools/check_role_routing_directive_evidence.py` to validate saved hard-directive adoption and explanation-only evidence.

#### Scenario: Explicit directive is adopted

- **WHEN** the user explicitly requests `omx` or `LangGraph`
- **AND** the capability chain, preflight, and task thresholds are satisfied
- **THEN** the activation trace SHALL report the requested lane as `selected` or `running`
- **AND** it SHALL NOT stay in explanation-only mode
- **AND** saved evidence SHALL pass the role/directive checker

#### Scenario: Explicit directive is blocked

- **WHEN** the user explicitly requests `omx` or `LangGraph`
- **AND** the requested lane cannot be adopted
- **THEN** the activation trace SHALL report `blocked:<reason>` or `threshold_not_met:<reason>`
- **AND** it SHALL NOT describe the directive as an optional preference

### Requirement: Smallest-sufficient role selection SHALL stay trigger-based

The orchestration activation policy SHALL select the smallest sufficient expert role set for the current phase. It SHALL NOT add roles merely because those roles are available. Bounded multi-face research SHALL start with homogeneous `analystxN` fan-out and SHALL escalate to `architect`, `planner`, or `writer` only after analyst fan-in exposes architecture, execution-ordering, or document-finalization work.

The repository SHALL provide `tools/check_role_routing_directive_evidence.py` to validate saved role-routing, role-minimality, and analyst-first evidence.

#### Scenario: Bounded multi-face research starts analyst-first

- **WHEN** the current task is bounded multi-face research
- **THEN** the first expert fan-out SHALL use `analystxN`
- **AND** it SHALL NOT include architect, planner, or writer by default before analyst fan-in
- **AND** saved evidence SHALL pass the role/directive checker

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

### Requirement: Native Codex SHALL remain the base layer and durable lanes SHALL be task-fit choices
Native Codex SHALL remain the base layer. oh-my-codex, native_omx, skills, profile helpers, and LangGraph SHALL be described as additive workflow or durable-state layers, not as Codex replacements. A durable task SHALL use one backend family at a time. Worker-centric durable execution, worktree isolation, mailbox flow, and direct worker lifecycle control SHALL justify `native_omx`; graph-shaped multi-phase execution, checkpoint-driven recovery, interrupt/resume approval gates, frozen briefs, and persisted survivor queues SHALL justify LangGraph.

Effective lane-fit evidence SHALL be script-checkable. The repository SHALL provide `tools/check_effective_lane_fit_evidence.py` to validate repository policy surfaces and saved run-summary evidence for native_omx worker-centric fit, LangGraph graph-shaped fit, default-backend-not-enough decisions, and explicit close/handoff before backend-family switching.

#### Scenario: Effective lane differs from default backend
- **WHEN** LangGraph is ready but the task is worker-centric
- **THEN** activation MAY select `native_omx` as the effective lane with a named worker-centric reason
- **AND** it SHALL NOT mix `native_omx` worker lifecycle with LangGraph checkpoint state without explicit close or handoff
- **AND** saved lane-fit evidence SHALL pass `tools/check_effective_lane_fit_evidence.py`

#### Scenario: LangGraph lane is selected for graph-shaped work
- **WHEN** a durable task selects LangGraph as the effective lane
- **THEN** the evidence SHALL cite graph-shaped multi-phase execution, checkpoint-driven recovery, interrupt/resume approval gates, frozen briefs, persisted survivor queues, or equivalent graph-shaped fit
- **AND** it SHALL NOT rely only on `backend_default=langgraph` or backend readiness as the task-level adoption reason

#### Scenario: Backend family switching is explicit
- **WHEN** saved evidence mentions both `native_omx` and LangGraph in one durable task flow
- **THEN** it SHALL show one backend family for the active task or record explicit close/handoff before switching
- **AND** it SHALL fail lane-fit evidence if the switch is silent or implicit

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

### Requirement: Delegation and leader wait discipline SHALL be script-checkable

The orchestration activation policy SHALL require delegated expert or worker work to be concrete, bounded, self-contained, non-duplicative, and materially advancing while the current main Codex CLI session remains the leader.

The leader SHALL identify immediate critical-path local work before delegation, keep urgent blocking critical-path work local unless a handoff is explicitly recorded, continue meaningful non-overlapping leader work while experts run, and use `wait_agent` only when the next leader step is blocked by the delegated result.

The repository SHALL provide `tools/check_delegation_wait_discipline_evidence.py` to validate repository policy surfaces and saved run-summary or worker-brief evidence for delegation design, code-worker ownership, duplicate-work prevention, and leader wait discipline.

#### Scenario: Delegation evidence is validated

- **GIVEN** a saved run summary describes delegated expert or worker work
- **WHEN** the evidence checker is run against that summary
- **THEN** it SHALL fail if the summary omits immediate critical-path local work
- **AND** it SHALL fail if the delegated task is not described as concrete, bounded, self-contained sidecar work that materially advances the task
- **AND** it SHALL fail if duplicate-work prevention or non-overlapping ownership is missing
- **AND** it SHALL fail if code-changing worker delegation lacks file/module ownership, "not alone in the codebase" instructions, or changed-path reporting expectations

#### Scenario: Leader waits for delegated work

- **GIVEN** a saved run summary describes `wait_agent` or equivalent waiting for delegated work
- **WHEN** the evidence checker is run against that summary
- **THEN** it SHALL fail if the wait is indefinite, silent, or reflexive
- **AND** it SHALL require either meaningful non-overlapping leader work during the wait or a clear critical-path blocker explaining why the leader is blocked until the delegated result returns

### Requirement: Exploration, code-change delegation, and durable artifact persistence SHALL stay script-checkable

Read-only exploration SHALL be used for specific codebase questions, symbol mapping, or file discovery. It SHALL NOT replace a bounded code-changing worker task when a safe implementation patch is clear. LangGraph entrypoints and repo-local `.omx/state/langgraph/` state SHALL be used when graph phases, checkpoint gates, frozen briefs, survivor queues, or tracked LangGraph thread state are required. `.omx/state/selectors/active.json` SHALL remain the active selector authority for automatic durable-team adoption; compatibility records SHALL be context only. Durable artifacts, frozen briefs, and survivor queues SHALL be written to repo-local state or documented artifact paths rather than only transient chat context. The repository SHALL provide `tools/check_durable_artifact_state_surfaces.py` to validate repository policy surfaces and saved run-summary, worker-brief, or durable handoff evidence for these boundaries.

#### Scenario: Graph-shaped checkpoint work is selected

- **WHEN** the task requires checkpoint gates, frozen briefs, survivor queues, or tracked LangGraph thread state
- **THEN** the durable workflow SHALL use LangGraph entrypoints and repo-local `.omx/state/langgraph/` state
- **AND** the durable artifacts SHALL have documented artifact paths or repo-local state locations
- **AND** automatic durable-team adoption SHALL cite `.omx/state/selectors/active.json` rather than compatibility records alone

#### Scenario: Exploration does not replace bounded implementation

- **GIVEN** the implementation patch is clear and safe to delegate
- **WHEN** read-only exploration evidence is recorded
- **THEN** exploration SHALL remain specific, well-scoped, and read-only
- **AND** it SHALL NOT be the only evidence surface for the code-changing implementation task

#### Scenario: Durable handoff artifacts are persisted

- **WHEN** research fan-in creates a frozen implementation brief or adversarial review leaves survivor candidates
- **THEN** the brief or survivor queue SHALL be persisted to repo-local state or documented artifact paths
- **AND** it SHALL include the required handoff fields or debugger-lane follow-up evidence instead of existing only in transient chat context

### Requirement: Research handoff and adversarial review SHALL persist bounded handoffs
Open-ended work SHALL keep research and implementation in different roles. After research fan-in, the result SHALL be persisted as a frozen implementation brief with scope, non-goals, acceptance evidence, ownership boundaries, and unresolved risks before implementation starts. `bug-finder`, `bug-rebutter`, and `bug-judge` SHALL remain burst, read-only, leader-side roles. Their survivors SHALL be persisted as an adversarial-review survivor queue for debugger-lane follow-up instead of keeping the bug triad alive as persistent workers. LangGraph, AutoGen and CrewAI SHALL be treated as general programmable orchestration runtimes, not native Codex-subagent equivalents.

#### Scenario: Contested bug review leaves survivors
- **WHEN** normal verification leaves contested or high-volume bug candidates
- **THEN** burst bug-triad results SHALL be absorbed and closed
- **AND** unresolved survivors SHALL be persisted for debugger-lane follow-up rather than kept alive as persistent bug workers

### Requirement: Capability switch chains SHALL be executable-policy checked
The orchestration activation policy SHALL treat capability switches as a strict dependency chain and SHALL use `tools/check_capability_switch_chain.py` as executable policy support for present user-level state. `subagent_routing=off` SHALL require higher orchestration layers to be off, `oh_my_codex=off` SHALL require `langgraph=off`, and `durable_orchestration_backend=langgraph` SHALL require `langgraph=on`.

#### Scenario: Activation policy guard checks switch dependencies
- **WHEN** the orchestration activation policy guard runs
- **THEN** it SHALL invoke or embed the capability-switch dependency checker
- **AND** invalid present state combinations SHALL fail as capability-chain violations

### Requirement: Orchestration enforcement checkers are wired into shared CI

The repository SHALL run existing automatic-orchestration enforcement checker tests through the shared local/remote CI manifest, and SHALL run no-input orchestration guard checks from `tools/run_openspec_guard.py` when they can execute without synthetic task evidence.

#### Scenario: Local gate covers existing orchestration checker tests

- **GIVEN** `tools/ci/local_gate.ps1` is run
- **WHEN** it executes Python unit tests through `tools/ci/ci_test_manifest.json`
- **THEN** capability-switch, orchestration trace evidence, expert lifecycle/wait pacing, and custom-agent TOML schema tests are included in the manifest.

#### Scenario: OpenSpec guard runs capability-switch chain validation

- **GIVEN** `tools/run_openspec_guard.py --root . --json` is run
- **WHEN** user-level capability state and repo-local backend context are available or absent
- **THEN** `check_capability_switch_chain.py` is invoked as an OpenSpec guard step and reports violations or warnings through the guard payload.

### Requirement: Agent skill and profile surfaces SHALL remain distinct

The orchestration activation policy SHALL keep native Codex agents, workflow skills, plugin-provided skills, plugin modules, and profile helpers as distinct surfaces, and SHALL reject evidence that treats skill/profile invocation as native subagent or expert-result evidence.

#### Scenario: Repository policy surfaces distinguish execution surfaces

- **GIVEN** the repository OpenSpec guard runs
- **WHEN** it checks orchestration activation policy surfaces
- **THEN** the policy surfaces SHALL state that native agents are loaded from agent TOMLs, skills are loaded from `SKILL.md`, profile helpers change visible procedural context only, and skill/profile invocation is not expert evidence.

#### Scenario: Evidence rejects skill or profile claims as expert evidence

- **GIVEN** a saved routing report is checked
- **WHEN** it claims a skill invocation or plugin profile load as an expert returned result, native subagent, worker, or durable-team evidence
- **THEN** the checker SHALL fail that evidence unless it separately identifies an actual expert result, durable checkpoint, or local verification source.
