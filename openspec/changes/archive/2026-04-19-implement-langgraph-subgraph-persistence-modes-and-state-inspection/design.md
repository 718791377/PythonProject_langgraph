## Context

The repository already exposes a reusable subgraph library, active-subgraph posture, command-driven parent handoffs, streaming, memory, migration, and generalized live routing. What it still lacks is a first-class contract for how reusable subgraphs persist state between calls and when their state can be inspected.

The official LangGraph subgraphs guide is specific here:

- `checkpointer=None` means per-invocation persistence
- `checkpointer=True` means per-thread persistence
- `checkpointer=False` means stateless execution
- subgraph state inspection depends on persistence and static subgraph discoverability
- per-thread subgraphs do not support parallel calls to the same subgraph instance

## Goals / Non-Goals

**Goals:**

- define official subgraph persistence modes for the user-level LangGraph lane
- project subgraph-state inspection availability and constraints into operator-facing durable surfaces
- keep the rollout additive to the existing reusable subgraph library and generalized routing layers
- make the next implementation step concrete enough to land in Python contracts, CLI projections, installer helpers, and tests

**Non-Goals:**

- replacing the existing reusable subgraph library
- redesigning generalized live routing
- implementing every possible subgraph debugging surface in one pass
- introducing cloud-only or LangSmith-only inspection dependencies

## Decisions

### Decision 1: Model subgraph persistence modes explicitly instead of implying them from current reusable-subgraph posture

The current library surface says which subgraph is active, but not whether that subgraph is per-invocation, per-thread, or stateless. The new change should make that explicit.

### Decision 2: State inspection should be surfaced as bounded posture, not as an unbounded dump of nested checkpoints

The operator-facing surface should explain whether subgraph state is inspectable, why, and which helper to use. It should not attempt to dump arbitrary nested checkpoint payloads by default.

### Decision 3: Static discoverability and same-subgraph parallel-call constraints belong in the contract

The official doc includes two important constraints that should become contract-visible:

- stateless subgraphs do not expose persisted state
- per-thread persistence conflicts with parallel calls to the same subgraph instance

### Decision 4: Add a dedicated user-level inspection helper instead of burying the new posture behind unrelated wrappers

An additive helper keeps the new capability easy to inspect without weakening the existing `subgraphs` helper or the canonical durable-state summary.

## Risks / Trade-offs

- [Risk] The rollout could overclaim exact runtime parity while the local implementation remains bounded. -> Mitigation: describe the result as bounded persistence-mode and inspection posture rather than full subgraph-debugging parity.
- [Risk] Per-thread caveats may be easy to forget in later worker flows. -> Mitigation: make same-subgraph parallel-call constraints operator-visible.
- [Risk] Operator surfaces could become noisy if they dump too much nested state. -> Mitigation: keep the first rollout focused on mode, availability, constraints, and helper pointers.

## Validation Plan

1. Add proposal, design, tasks, and delta specs for subgraph persistence modes and state inspection.
2. Extend the LangGraph contract layer with explicit subgraph persistence-mode and inspection fields.
3. Add additive CLI/runtime projection and user-level helper surfaces for subgraph-state inspection.
4. Validate the new posture in Python and installer integration tests without regressing current reusable-subgraph or generalized-routing surfaces.
