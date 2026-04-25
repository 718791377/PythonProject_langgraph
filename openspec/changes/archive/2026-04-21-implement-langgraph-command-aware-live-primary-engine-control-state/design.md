## Context

The current LangGraph lane already exposes graph-kernel posture, primary-runtime engine posture, compiled invocation, live execution, fuller live primary execution semantics, superstep traces, stateful transition posture, graph-resident boundary-state handling, subgraph-aware handoff-state handling, approval-aware resume-state handling, recovery-aware provenance-state handling, durable-artifact-aware live-engine state handling, and reducer-aware merge-state handling.

What still remains intentionally bounded is command-aware control state inside the live primary engine itself. The current live-engine line still relies on an adjacent command projection for transition kind, update keys, goto target, graph scope, source subgraph, target subgraph, parent-handoff target, resume posture, and resume payload keys.

## Goals / Non-Goals

**Goals:**

- deepen the live primary-engine beyond the current reducer-aware merge-state posture into command-aware control-state handling
- preserve the seven-phase operator shell, durable artifacts, and current helper surfaces
- keep the result inspectable through the current user-level helper surfaces
- make the next live-engine step concrete enough to land in contracts, CLI, installer, and tests

**Non-Goals:**

- replacing the current leader model
- replacing `native_omx`
- reopening automatic-policy expansion in the same change
- claiming that the whole LangGraph lane is now fully generalized and unbounded

## Decisions

### Decision 1: Continue evolving the live primary engine rather than adding another projection-only layer

The remaining gap is command-aware live-engine control state, not another adjacent command wrapper.

### Decision 2: Preserve the current user-facing shell

The existing seven-phase shell remains the stable operator contract; deeper command-aware behavior should drive it, not replace it.

## Validation Plan

1. Define proposal, design, tasks, and delta specs for command-aware live primary-engine control-state semantics.
2. Extend the Python LangGraph contract and runtime layer with command-aware posture.
3. Expose additive user-level projection and helper surfaces for the new engine behavior.
4. Validate the new posture without regressing current routing, subgraph, policy, artifact, reducer, or replay surfaces.
