## Context

The current LangGraph lane already exposes graph-kernel posture, primary-runtime engine posture, compiled invocation, live execution, fuller live primary execution semantics, deeper projected path semantics, reusable subgraphs, subgraph persistence modes, generalized live routing, and broader automatic runtime-policy posture.

What still remains intentionally bounded is the compiled live primary engine itself. The current `deeper-engine` lane can compute a richer future path, but the compiled graph branch is still a single passthrough node instead of a superstep-aware multi-node graph path.

## Goals / Non-Goals

**Goals:**

- add an additive superstep-aware live primary-engine lane beyond the current deeper projected-path posture
- preserve the seven-phase operator shell and existing durable artifacts
- keep the result inspectable through the current user-level helper surfaces
- make the next live-engine step concrete enough to land in contracts, CLI, installer, and tests

**Non-Goals:**

- replacing the current leader model
- replacing `native_omx`
- reopening automatic-policy expansion in the same change
- claiming that the whole LangGraph lane is now fully generalized and unbounded

## Decisions

### Decision 1: Add a new live-engine lane instead of mutating `deeper-engine` destructively

The recent LangGraph deepening work has used additive lanes and helper surfaces rather than silently repurposing older ones. This change continues that pattern by adding a `superstep-engine` lane rather than redefining `deeper-engine` in place.

### Decision 2: Reuse accepted routing and boundary semantics

The new lane should reuse the already accepted command, loop, interrupt, recovery, terminal, and recursion-limit semantics rather than inventing a competing phase model.

### Decision 3: Make the compiled graph branch multi-node and superstep-aware

The new lane should move beyond a single passthrough compiled node and traverse a bounded multi-node path so the resulting projection can expose superstep-aware node and phase visit traces.

## Validation Plan

1. Define proposal, design, tasks, and delta specs for superstep live primary-engine semantics.
2. Extend the Python LangGraph contract and runtime layer with a superstep-aware live-engine lane.
3. Expose additive user-level projection and helper surfaces for the superstep live-engine behavior.
4. Validate the new posture without regressing current routing, subgraph, policy, or durable-artifact surfaces.
