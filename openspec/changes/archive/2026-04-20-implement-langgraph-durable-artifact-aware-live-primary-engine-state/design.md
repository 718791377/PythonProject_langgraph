## Context

The current LangGraph lane already exposes graph-kernel posture, primary-runtime engine posture, compiled invocation, live execution, fuller live primary execution semantics, superstep traces, stateful transition posture, graph-resident boundary-state handling, subgraph-aware handoff-state handling, approval-aware resume-state handling, and recovery-aware provenance-state handling.

What still remains intentionally bounded is the durable-artifact state of the live primary engine itself. The current live-engine line still relies on adjacent artifact surfaces for implementation-brief presence, survivor-queue presence, and artifact-level summary posture.

## Goals / Non-Goals

**Goals:**

- deepen the live primary-engine beyond the current recovery-aware provenance-state posture into durable-artifact-aware handling
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

The remaining gap is durable-artifact-aware engine state, not another projection-only surface.

### Decision 2: Preserve the current user-facing shell

The existing seven-phase shell remains the stable operator contract; deeper durable-artifact-aware behavior should drive it, not replace it.

## Validation Plan

1. Define proposal, design, tasks, and delta specs for durable-artifact-aware live primary-engine semantics.
2. Extend the Python LangGraph contract and runtime layer with artifact-aware posture.
3. Expose additive user-level projection and helper surfaces for the new engine behavior.
4. Validate the new posture without regressing current routing, subgraph, policy, or durable-artifact surfaces.
