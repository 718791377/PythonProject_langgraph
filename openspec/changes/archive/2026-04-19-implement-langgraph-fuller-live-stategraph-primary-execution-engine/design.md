## Context

The current LangGraph lane already exposes graph-kernel posture, primary-runtime engine posture, compiled invocation, live execution, generalized routing, reusable subgraphs, subgraph persistence modes, interrupts, replay, recovery, streaming, memory, and migration posture.

What still remains intentionally bounded is the live execution engine itself. The current rollout can report and request execution posture, but it does not yet behave like a fuller graph-native primary execution engine with richer execution semantics.

## Goals / Non-Goals

**Goals:**

- move from bounded live-execution posture toward a fuller live `StateGraph` primary execution engine
- preserve the current seven-phase operator shell and current durable artifacts during the rollout
- keep the result inspectable through the current user-level helper surfaces
- make the next runtime implementation step concrete enough to land in contracts, CLI, installer, and tests

**Non-Goals:**

- replacing the current leader model
- replacing `native_omx`
- landing every future automation policy in the same change
- hiding boundedness where it still remains

## Decisions

### Decision 1: Evolve the live execution engine rather than invent another metadata-only layer

The remaining gap is execution semantics, not one more descriptive projection layer.

### Decision 2: Preserve the existing operator shell while deepening engine behavior underneath it

The current seven-phase shell remains the stable user-facing contract. The fuller engine should drive that shell, not replace it.

### Decision 3: Keep durable-state and helper surfaces compatibility-aware

The richer engine should remain visible through the current inspectable durable-state surface and user-level wrappers instead of creating a disconnected inspection plane.

## Validation Plan

1. Define proposal, design, tasks, and delta specs for the fuller primary execution-engine step.
2. Extend the Python LangGraph contract and runtime layer with fuller primary execution-engine posture.
3. Expose additive user-level projection and helper surfaces for the richer engine behavior.
4. Validate the new posture without regressing current generalized-routing, subgraph, or durable-artifact surfaces.
