## Context

The current user-level Codex / oh-my-codex workflow already has wrapped startup, leader-side native subagent routing, durable worker execution through `omx team`, native Windows durable-team backend support, and repo-local `.omx` runtime isolation. What it still lacks is a graph-shaped persistence kernel for checkpointed long-running execution, interrupt/resume approval gates, persisted research handoff, and persisted adversarial-review survivor queues.

LangGraph is a strong fit because its official capabilities center on long-running, stateful orchestration with persistence, interrupts, memory, and subgraphs. The intended integration is additive: keep Codex / oh-my-codex as the operator-facing leader and control plane, and let LangGraph act as the persistent orchestration backend under that layer.

## Goals / Non-Goals

**Goals:**

- integrate LangGraph as an optional durable orchestration backend under the existing Codex / oh-my-codex workflow
- preserve leader-side native subagents and homogeneous durable worker defaults
- formalize a seven-phase root graph plus reusable subgraphs
- persist research-to-implementation handoff and adversarial-review survivor queues
- bridge LangGraph runtime state into the existing `.omx` state model
- keep backend choice explicit and operator-visible

**Non-Goals:**

- replacing Codex with LangGraph
- removing the current direct `omx team` path
- making research roles or bug-triad roles default persistent workers
- introducing a mixed persistent pane default
- requiring LangSmith Deployment, Agent Server, or cloud infrastructure in the first rollout

## Decisions

### Decision 1: LangGraph is a backend augmentation, not a platform replacement

LangGraph will sit under the existing Codex / oh-my-codex flow:

- Codex CLI remains the leader and final integrator
- oh-my-codex remains the user-level control and workflow layer
- LangGraph becomes the durable orchestration kernel for selected long-running tasks

### Decision 2: Use a Python sidecar service as the first implementation shape

The first implementation should be a Python LangGraph sidecar that runs on native Windows and is called through additive entrypoints.

Why:

- LangGraph’s official Python surface is directly aligned with persistence, interrupts, and subgraphs
- it keeps the orchestration layer separate from the user-level PowerShell wrappers
- it avoids forcing the leader session to host graph state directly

### Decision 3: Use repo-local thread identity and checkpoint storage

The first durable identity model will use a repo-local thread namespace such as:

- `thread_id = <repo-hash>:<worktree-id>:<task-id>`

The first persistence backend should be local and simple:

- SQLite-backed checkpointer or equivalent local durable storage
- state files and metadata rooted under `.omx/state/langgraph/`

### Decision 4: Mirror the existing seven-phase development flow in a root graph

The root graph should follow the already adopted development phases:

- define-target
- read-context
- freeze-plan
- execute-parallel
- integrate-converge
- stabilize
- verify-accept

Conditional transitions should allow early-phase no-team execution, execution-to-stabilization escalation, and verification failure loops back to stabilization.

### Decision 5: Use subgraphs for role families, not one long-lived graph per role

The first LangGraph design should favor a small number of reusable subgraphs:

- research subgraph
- planning subgraph
- execution subgraph
- verification subgraph
- adversarial-review subgraph

This matches the current “persistent execution, bursty experts” operating model and prevents every specialist role from becoming an always-on durable worker.

### Decision 6: Research handoff is a persisted object, not a persistent research team

Research results should be persisted as a frozen implementation brief with fields such as:

- objective
- non-goals
- accepted decisions
- constraints
- interfaces
- ownership boundaries
- acceptance criteria
- validation plan

Execution must then continue from a fresh implementation context that consumes the brief rather than the full open-ended research history.

### Decision 7: Adversarial bug review is a persisted survivor queue, not a persistent triad

`bug-finder`, `bug-rebutter`, and `bug-judge` remain bursty expert calls.

What persists is:

- candidate-set metadata
- judge survivors
- debugger-lane ownership
- fix / verify status

The debugger lane can remain durable, but the bug triad itself should not become a default persistent team.

### Decision 8: The `.omx` bridge remains the source of repo-local runtime discovery

LangGraph state should align to `.omx` instead of inventing a separate repo-local runtime root.

Recommended layout:

- `.omx/state/langgraph/threads/`
- `.omx/state/langgraph/checkpoints/`
- `.omx/state/langgraph/interrupts/`
- `.omx/state/langgraph/store/`
- `.omx/state/langgraph/backend.json`

## Risks / Trade-offs

- [Risk] Two durable backends may confuse operators. → Mitigation: add an explicit backend selector and clear playbook language.
- [Risk] LangGraph persistence may overlap with existing `.omx` state and create duplicate truth. → Mitigation: keep `.omx` as the runtime root and define one clear bridge contract.
- [Risk] Research handoff may still leak too much context into execution. → Mitigation: require a frozen brief and a fresh execution context boundary.
- [Risk] Adversarial-review persistence could grow noisy if every candidate bug is stored durably. → Mitigation: persist only judge-approved survivors by default.
- [Risk] Interrupt and resume flows may increase operator burden. → Mitigation: limit interrupts to explicit approval points such as plan freeze, risky stabilize steps, and failed final verification.

## Migration Plan

1. Add control-surface requirements for selecting LangGraph as a durable backend.
2. Add LangGraph-oriented entrypoint requirements and playbook rules.
3. Implement a minimal Python sidecar with one root graph, local persistence, and repo-local thread identity.
4. Add the research brief persistence layer and execution restart boundary.
5. Add the adversarial-review survivor queue and debugger-lane consumption path.
6. Validate restart, resume, interrupt, and cross-repository isolation.
7. Keep the current direct `omx team` path available as fallback until LangGraph is proven stable.

## Open Questions

- Should the backend selector be global, repo-local, or both?
- Should the first persistence backend be SQLite file-based only, or should a Postgres-backed option be allowed immediately?
- Should execution use one durable LangGraph thread per task, or a root thread plus per-slice execution threads?
- Should the first rollout expose LangGraph through new entrypoint names only, or also through the existing automatic durable routing helper?
