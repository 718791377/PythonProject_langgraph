## Context

The current LangGraph lane already exposes graph-kernel posture, primary-runtime engine posture, compiled invocation, live execution, fuller live primary execution semantics, deeper projected-path semantics, broader automatic runtime-policy posture, and a superstep-aware live primary-engine lane that can traverse a bounded multi-node compiled graph path.

What still remains intentionally bounded is the statefulness of the compiled live primary engine itself. The current superstep lane can execute a prepared path, but it still does not carry more of the routing and continuation semantics inside the graph-native execution state itself.

## Goals / Non-Goals

**Goals:**

- deepen the live primary-engine beyond the current prepared superstep trace posture
- preserve the seven-phase operator shell and existing durable artifacts
- keep the result inspectable through the current user-level helper surfaces
- make the next live-engine step concrete enough to land in contracts, CLI, installer, and tests

**Non-Goals:**

- replacing the current leader model
- replacing `native_omx`
- reopening automatic-policy expansion in the same change
- claiming that the whole LangGraph lane is now fully generalized and unbounded

## Decisions

### Decision 1: Continue evolving the live primary engine rather than inventing another metadata-only lane

The remaining gap is stateful graph-native execution semantics, not another projection-only wrapper.

### Decision 2: Preserve the current user-facing shell

The existing seven-phase shell remains the stable operator contract; deeper stateful engine behavior should drive it, not replace it.

## Validation Plan

1. Define proposal, design, tasks, and delta specs for stateful live primary-engine semantics.
2. Extend the Python LangGraph contract and runtime layer with stateful live-engine posture.
3. Expose additive user-level projection and helper surfaces for the stateful engine behavior.
4. Validate the new posture without regressing current routing, subgraph, policy, or durable-artifact surfaces.
