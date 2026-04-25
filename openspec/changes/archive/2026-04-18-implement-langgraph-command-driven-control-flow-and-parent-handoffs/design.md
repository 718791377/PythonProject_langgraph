## Context

The current user-level LangGraph lane already persists thread state, checkpoints, interrupts, replay or recovery posture, reducer-aware branch merges, and reusable subgraph contracts. It also exposes a canonical inspectable durable-state surface and additive user-level helper wrappers.

What remains missing is the official LangGraph control-flow layer centered on `Command`. Today the local lane still expresses most durable movement through phase changes, loop verdicts, and helper-specific mutation paths. That is workable, but it does not yet model:

- explicit combined state update plus routing decisions
- parent-graph transitions from inside reusable subgraphs
- inspectable parent-handoff attribution across subgraph boundaries
- command-driven resume payload posture as a first-class durable object

The current bottleneck is therefore not durable persistence or subgraph reuse by themselves. The bottleneck is the missing command-driven transition contract that lets reusable subgraphs hand work back to the parent graph in a graph-native, inspectable, and source-attributed way.

## Goals / Non-Goals

**Goals:**

- define a user-level LangGraph command-driven control-flow contract
- define explicit parent-directed handoff posture for reusable subgraphs
- persist command-driven transition metadata in tracked LangGraph thread and checkpoint state
- expose command-driven transition and parent-handoff posture through the canonical inspectable durable-state surface
- keep the command model additive under the existing Codex CLI leader and oh-my-codex workflow layer

**Non-Goals:**

- changing when `langgraph` is selected as the effective durable backend
- replacing the seven-phase root graph with a free-form arbitrary node graph
- turning replay, recovery, or loop controls into a generic raw-state editor
- making subgraphs directly user-launchable as independent always-on durable teams
- introducing LangSmith-only or cloud-only orchestration dependencies

## Decisions

### Decision 1: Keep conditional edges and add command-driven transitions as an additive control primitive

The current lane already uses structured gate verdicts and phase-driven movement. Replacing all of that with a pure `Command`-only model would expand scope and destabilize already-delivered loop and recovery behavior.

The first rollout should therefore keep existing conditional-edge behavior, while adding a command envelope that can record:

- state updates
- local `goto` target
- parent-graph target when relevant
- resume payload posture
- source and target subgraph identity

Alternative considered:

- rewrite the current local runtime around a single command-only transition model
  - rejected because it would reopen quality-loop and replay or recovery behavior that is already in place

### Decision 2: Parent handoffs must be explicit subgraph-boundary operations, not inferred side effects

Reusable subgraphs already declare role families and handoff boundaries. Parent-directed handoffs should refine that contract instead of bypassing it.

Each supported parent handoff should therefore remain explicit about:

- source subgraph
- target graph scope
- target node or phase family
- carried state update
- whether resume input is involved

Alternative considered:

- infer parent handoffs from phase changes alone
  - rejected because the point of this change is to make graph-native routing explicit rather than hidden in phase inference

### Decision 3: Command-driven resume posture must remain inspectable and bounded

Official LangGraph treats resume as part of the command/control surface. The local user-level lane should therefore record whether an interrupted thread is waiting for:

- ordinary resume
- resume with explicit payload
- parent-directed return after approval

The first rollout should expose resume posture and payload-presence metadata, but not become a generic arbitrary-input tunnel.

Alternative considered:

- keep resume as an opaque helper-only action with no durable projection
  - rejected because command-driven routing is not credible if operator-visible resume posture remains invisible

### Decision 4: Inspectable state should project command posture without forcing a new mutation plane

This repository already has a canonical durable-state summary and additive helper pointers. The command-driven layer should extend that surface rather than create a second competing operator surface.

The first rollout should expose:

- active command transition kind
- source and target subgraph identity when present
- local versus parent graph target scope
- explicit helper pointer for subgraph-aware inspection when relevant

Alternative considered:

- add a separate dedicated command-only wrapper before projecting the new state canonically
  - rejected because command posture belongs in the same inspectable durable-state story as loops, recovery, and reducers

### Decision 5: The first rollout should target contract fidelity and inspectability before generalized execution freedom

The initial goal is not to support every possible official LangGraph graph shape. The goal is to make command-driven routing and parent handoffs first-class, inspectable, and durable in the user-level lane.

That means the first rollout should prioritize:

- stable contract fields
- durable state persistence
- explicit projection in inspect surfaces
- bounded implementation over the current reusable subgraph families

Alternative considered:

- immediately expose arbitrary command-driven cross-graph execution without bounded subgraph families
  - rejected because it would blur operator intent, overexpand scope, and weaken current mainline sequencing discipline

## Risks / Trade-offs

- [Risk] Command-driven transition metadata may duplicate existing loop or recovery fields. -> Mitigation: keep command posture scoped to transition and handoff semantics, not to broad execution-state replacement.
- [Risk] Parent handoffs may weaken explicit research or implementation boundaries. -> Mitigation: require subgraph contracts to declare permitted parent-exit boundaries and preserve fresh-context rules.
- [Risk] Resume payload posture may drift toward unbounded raw-state injection. -> Mitigation: model payload presence and target scope first, while keeping mutation bounded by existing recovery and interrupt contracts.
- [Risk] Inspectable state may become noisy if every transition detail is projected. -> Mitigation: project only stable operator-facing command fields and keep lower-level internal transition detail out of the canonical summary.

## Migration Plan

1. Add proposal, design, and delta spec artifacts for command-driven control flow and parent handoffs.
2. Extend the LangGraph contract layer with stable command envelope and target-scope fields.
3. Extend tracked thread and checkpoint state with command-driven transition posture and parent-handoff attribution.
4. Extend inspectable durable-state projection and existing helper pointers with command-aware fields.
5. Validate additive behavior against the current reusable subgraph lane without reopening backend selection or existing durable-artifact policy.

Rollback strategy:

- revert the command-driven envelope and parent-handoff projection fields only
- keep reusable subgraph contracts, loops, replay or recovery controls, and reducer semantics intact

## Open Questions

- Should the first rollout surface the last applied command only, or also a small rolling transition history in checkpoint metadata?
- Should command-driven parent handoffs allow direct cross-subgraph jumps, or only subgraph-to-parent-to-subgraph movement in the first rollout?
- Should resume payload posture be exposed as payload-present or payload-absent only, or should the first rollout also classify payload kinds?
