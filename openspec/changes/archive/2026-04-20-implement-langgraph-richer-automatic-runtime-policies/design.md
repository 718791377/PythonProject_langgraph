## Context

The current LangGraph lane can already expose graph-kernel posture, primary-runtime engine posture, compiled invocation, live execution, fuller live primary execution semantics, generalized routing, reusable subgraphs, subgraph persistence modes, interrupts, replay, recovery, streaming, memory, and migration posture.

What still remains intentionally manual-first is runtime policy. The current user-level lane can show posture and helpers, but it does not yet expose bounded automatic-policy behavior for areas like migration handling or approval-queue resolution.

## Goals / Non-Goals

**Goals:**

- add bounded automatic runtime-policy posture to the current LangGraph lane
- keep the result explicit, inspectable, and safe by default
- focus on concrete policy domains already called out by the implementation plan
- make the next runtime-policy step concrete enough to land in contracts, CLI, installer, and tests

**Non-Goals:**

- replacing manual operator control
- silently auto-switching backend family
- adding cloud-only orchestration dependencies
- turning the lane into an unbounded autonomous policy engine

## Decisions

### Decision 1: Expose policy posture explicitly before expanding policy scope

Automatic behavior should be inspectable and bounded rather than implicit.

### Decision 2: Keep migration and approval policies in scope, leave broader policy families for later

The implementation plan already calls out automatic migration handling and queue-resolution behavior as the clearest remaining examples. This change should stay centered there.

### Decision 3: Preserve manual-first defaults

Automatic policy should remain additive and bounded. The operator should still be able to see and override the behavior.

## Validation Plan

1. Define proposal, design, tasks, and delta specs for richer automatic runtime policies.
2. Extend the Python LangGraph contract and runtime layer with bounded automatic-policy posture.
3. Expose additive user-level projection and helper surfaces for that policy layer.
4. Validate the new posture without regressing current engine, routing, subgraph, or durable-artifact surfaces.
