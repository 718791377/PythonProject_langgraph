## Context

The current LangGraph lane already exposes graph-kernel posture, primary-runtime engine posture, compiled invocation, live execution, fuller live primary execution semantics, deeper projected-path semantics, superstep-aware execution traces, stateful transition posture, and graph-resident boundary-state handling.

What still remains intentionally bounded is the subgraph and handoff state of the live primary engine itself. The current live-engine line still relies on adjacent command and subgraph projections for explicit parent handoffs and subgraph-aware continuation posture.

## Goals / Non-Goals

**Goals:**

- deepen the live primary-engine beyond the current graph-resident boundary-state posture into subgraph-aware handoff-state handling
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

The remaining gap is subgraph-aware handoff semantics, not another projection-only surface.

### Decision 2: Preserve the current user-facing shell

The existing seven-phase shell remains the stable operator contract; deeper subgraph-aware handoff behavior should drive it, not replace it.

## Validation Plan

1. Define proposal, design, tasks, and delta specs for subgraph-aware live primary-engine handoff-state semantics.
2. Extend the Python LangGraph contract and runtime layer with subgraph-aware handoff posture.
3. Expose additive user-level projection and helper surfaces for the new engine behavior.
4. Validate the new posture without regressing current routing, subgraph, policy, or durable-artifact surfaces.
