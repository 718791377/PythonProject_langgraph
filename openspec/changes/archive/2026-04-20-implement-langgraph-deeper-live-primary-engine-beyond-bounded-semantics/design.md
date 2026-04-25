## Context

The current LangGraph lane already exposes graph-kernel posture, primary-runtime engine posture, compiled invocation, live execution, fuller live primary execution semantics, reusable subgraphs, subgraph persistence modes, richer automatic runtime-policy posture, and the existing durable artifact surfaces.

What still remains intentionally bounded is the live primary engine itself. The current rollout can project richer execution posture, but it still does not behave like a deeper live engine beyond the current bounded semantics.

## Goals / Non-Goals

**Goals:**

- deepen the live primary-engine beyond the current bounded execution semantics
- preserve the seven-phase operator shell and existing durable artifacts
- keep the result inspectable through the current user-level helper surfaces
- make the next live-engine step concrete enough to land in contracts, CLI, installer, and tests

**Non-Goals:**

- replacing the current leader model
- replacing `native_omx`
- landing every future runtime policy or subgraph-expansion idea in the same change
- hiding remaining boundedness where it still exists

## Decisions

### Decision 1: Continue evolving the live primary engine rather than inventing another metadata-only layer

The remaining gap is deeper execution semantics, not another descriptive projection-only surface.

### Decision 2: Preserve the current user-facing shell

The existing seven-phase shell remains the stable operator contract; deeper engine behavior should drive it, not replace it.

## Validation Plan

1. Define proposal, design, tasks, and delta specs for deeper live primary-engine semantics.
2. Extend the Python LangGraph contract and runtime layer with deeper engine posture.
3. Expose additive user-level projection and helper surfaces for the deeper engine behavior.
4. Validate the new posture without regressing current routing, subgraph, policy, or durable-artifact surfaces.
