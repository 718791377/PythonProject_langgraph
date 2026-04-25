## Context

The current LangGraph lane already exposes graph-kernel posture, primary-runtime engine posture, compiled invocation, live execution, fuller live primary execution semantics, deeper projected-path semantics, superstep-aware execution traces, and a stateful live primary-engine lane that carries next-hop decisions and transition logs in graph-native execution state.

What still remains intentionally bounded is the boundary state of the compiled live primary engine itself. The current stateful lane still handles interrupt, recovery, and terminal boundary posture outside the compiled graph before graph-native execution begins.

## Goals / Non-Goals

**Goals:**

- deepen the live primary-engine beyond the current stateful transition posture into graph-resident boundary-state handling
- preserve the seven-phase operator shell and existing durable artifacts
- keep the result inspectable through the current user-level helper surfaces
- make the next live-engine step concrete enough to land in contracts, CLI, installer, and tests

**Non-Goals:**

- replacing the current leader model
- replacing `native_omx`
- reopening automatic-policy expansion in the same change
- claiming that the whole LangGraph lane is now fully generalized and unbounded

## Decisions

### Decision 1: Continue evolving the live primary engine rather than branching into another metadata-only wrapper

The remaining gap is graph-resident boundary handling, not another projection-only surface.

### Decision 2: Preserve the current user-facing shell

The existing seven-phase shell remains the stable operator contract; deeper graph-resident boundary-state behavior should drive it, not replace it.

## Validation Plan

1. Define proposal, design, tasks, and delta specs for graph-resident live primary-engine boundary-state semantics.
2. Extend the Python LangGraph contract and runtime layer with graph-resident boundary-state posture.
3. Expose additive user-level projection and helper surfaces for the new engine behavior.
4. Validate the new posture without regressing current routing, subgraph, policy, or durable-artifact surfaces.
