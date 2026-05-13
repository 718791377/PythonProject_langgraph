## ADDED Requirements

### Requirement: Smallest-sufficient role selection SHALL stay trigger-based
The orchestration activation policy SHALL select the smallest sufficient expert role set for the current phase. It SHALL NOT add roles merely because those roles are available. Bounded multi-face research SHALL start with homogeneous `analystxN` fan-out and SHALL escalate to `architect`, `planner`, or `writer` only after analyst fan-in exposes architecture, execution-ordering, or document-finalization work.

#### Scenario: Bounded multi-face research starts analyst-first
- **WHEN** the current task is bounded multi-face research
- **THEN** the first expert fan-out SHALL use `analystxN`
- **AND** it SHALL NOT include architect, planner, or writer by default before analyst fan-in

### Requirement: Agent, skill, profile, and follow-up surfaces SHALL stay distinct
The orchestration activation policy SHALL keep native Codex subagents, workflow skills, plugin-provided skills, profile helpers, durable workers, and LangGraph nodes as distinct execution surfaces. Skills SHALL load from `SKILL.md` files and skills are not native subagents. Profile hard-load or soft-load SHALL NOT by itself start durable workers or satisfy persistent-team thresholds. Follow-up work after a completed and absorbed expert SHALL spawn a fresh agent unless the user explicitly asks to preserve the thread or a plan records a preserved-thread reason.

#### Scenario: A skill is invoked during an activation flow
- **WHEN** a workflow skill or plugin profile is used
- **THEN** the final evidence label SHALL NOT treat that invocation as a returned native expert result
- **AND** any later expert follow-up SHALL use a fresh agent unless preservation is explicit

### Requirement: The main Codex CLI session SHALL remain the leader
The current main Codex CLI session SHALL remain the leader for activation checks, role selection, worker briefs, fan-in, evidence labeling, final integration, and release recommendations. Orchestration SHALL NOT require a separate persistent leader pane, and workers, skills, plugin profiles, and LangGraph nodes SHALL NOT become independent release authorities. Adoption decisions SHALL be scoped to the current task flow rather than whether the repository is newly created.

#### Scenario: Existing project resumes work
- **WHEN** an existing project or legacy resumed session continues a task flow
- **THEN** the main session SHALL apply current repository governance and capability-chain policy
- **AND** it SHALL keep local mainline and publication decisions under user-authorized leader control

### Requirement: Native Codex SHALL remain the base layer and durable lanes SHALL be task-fit choices
Native Codex SHALL remain the base layer. oh-my-codex, native_omx, skills, profile helpers, and LangGraph SHALL be described as additive workflow or durable-state layers, not as Codex replacements. A durable task SHALL use one backend family at a time. Worker-centric durable execution, worktree isolation, mailbox flow, and direct worker lifecycle control SHALL justify `native_omx`; graph-shaped multi-phase execution, checkpoint-driven recovery, interrupt/resume approval gates, frozen briefs, and persisted survivor queues SHALL justify LangGraph.

#### Scenario: Effective lane differs from default backend
- **WHEN** LangGraph is ready but the task is worker-centric
- **THEN** activation MAY select `native_omx` as the effective lane with a named worker-centric reason
- **AND** it SHALL NOT mix `native_omx` worker lifecycle with LangGraph checkpoint state without explicit close or handoff

### Requirement: Delegation SHALL preserve critical-path leader work
Delegation SHALL be concrete, bounded, self-contained, and materially advancing. The leader SHALL identify immediate critical-path work before delegating, SHALL NOT delegate urgent blocking work when the next leader action depends on the result, SHALL avoid duplicate leader/expert or expert/expert work, SHALL continue meaningful non-overlapping leader work while delegated work runs, and SHALL use `wait_agent` sparingly.

#### Scenario: A sidecar expert is running
- **WHEN** delegated sidecar work is in progress
- **THEN** the leader SHALL continue non-overlapping local work or record why it is blocked
- **AND** it SHALL not claim the delegated result as accepted without review and evidence labeling

### Requirement: Exploration, code-change delegation, and durable artifact persistence SHALL stay distinct
Read-only exploration SHALL be used for specific codebase questions, symbol mapping, or file discovery. It SHALL NOT replace a bounded code-changing worker task when a safe implementation patch is clear. LangGraph entrypoints and repo-local `.omx/state/langgraph/` state SHALL be used when graph phases, checkpoint gates, frozen briefs, survivor queues, or tracked LangGraph thread state are required. Durable artifacts, frozen briefs, and survivor queues SHALL be written to repo-local state or documented artifact paths rather than only transient chat context.

#### Scenario: Graph-shaped checkpoint work is selected
- **WHEN** the task requires checkpoint gates, frozen briefs, or survivor queues
- **THEN** the durable workflow SHALL use LangGraph entrypoints and repo-local `.omx/state/langgraph/` state
- **AND** the durable artifacts SHALL have documented artifact paths or repo-local state locations

### Requirement: Research handoff and adversarial review SHALL persist bounded handoffs
Open-ended work SHALL keep research and implementation in different roles. After research fan-in, the result SHALL be persisted as a frozen implementation brief with scope, non-goals, acceptance evidence, ownership boundaries, and unresolved risks before implementation starts. `bug-finder`, `bug-rebutter`, and `bug-judge` SHALL remain burst, read-only, leader-side roles. Their survivors SHALL be persisted as an adversarial-review survivor queue for debugger-lane follow-up instead of keeping the bug triad alive as persistent workers. LangGraph, AutoGen and CrewAI SHALL be treated as general programmable orchestration runtimes, not native Codex-subagent equivalents.

#### Scenario: Contested bug review leaves survivors
- **WHEN** normal verification leaves contested or high-volume bug candidates
- **THEN** burst bug-triad results SHALL be absorbed and closed
- **AND** unresolved survivors SHALL be persisted for debugger-lane follow-up rather than kept alive as persistent bug workers
