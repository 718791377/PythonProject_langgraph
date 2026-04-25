## Context

The current LangGraph lane already exposes graph-kernel posture, primary-runtime engine posture, compiled invocation, live execution, fuller live primary execution semantics, superstep traces, stateful transition posture, graph-resident boundary-state handling, subgraph-aware handoff-state handling, approval-aware resume-state handling, recovery-aware provenance-state handling, durable-artifact-aware live-engine state handling, reducer-aware merge-state handling, and command-aware control-state handling.

What still remains intentionally bounded is runtime-aware context and store state inside the live primary engine itself. The current live-engine line still relies on an adjacent runtime injection projection for context schema, runtime-context presence, runtime-context keys, runtime-context kind hints, store configuration, store access expectations, and store kind.

## Goals / Non-Goals

**Goals:**

- deepen the live primary-engine beyond the current command-aware control-state posture into runtime-aware context-store handling
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

The remaining gap is runtime-aware live-engine context and store state, not another adjacent runtime wrapper.

### Decision 2: Preserve the current user-facing shell

The existing seven-phase shell remains the stable operator contract; deeper runtime-aware behavior should drive it, not replace it.

## Validation Plan

1. Define proposal, design, tasks, and delta specs for runtime-aware live primary-engine context-store semantics.
2. Extend the Python LangGraph contract and runtime layer with runtime-aware posture.
3. Expose additive user-level projection and helper surfaces for the new engine behavior.
4. Validate the new posture without regressing current routing, subgraph, policy, artifact, reducer, command, or replay surfaces.
