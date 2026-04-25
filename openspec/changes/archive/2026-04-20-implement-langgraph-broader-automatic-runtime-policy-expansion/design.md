## Context

The current LangGraph lane already exposes a bounded automatic runtime-policy layer for safe migration continuation and safe resolved-queue auto-resume. What still remains intentionally bounded is the overall policy scope. The next step is not to remove operator control, but to broaden the bounded policy family in a controlled, inspectable way.

## Goals / Non-Goals

**Goals:**

- broaden the bounded automatic runtime-policy layer while keeping it inspectable and manual-first
- stay focused on concrete LangGraph runtime-policy behavior rather than reopening engine or routing work
- make the next automatic-policy step concrete enough to land in contracts, CLI, installer, and tests

**Non-Goals:**

- replacing manual operator control
- silently auto-switching backend family
- adding cloud-only orchestration dependencies
- turning the lane into an unbounded autonomous policy engine

## Decisions

### Decision 1: Evolve the current automatic-policy layer instead of inventing a disconnected policy plane

The current bounded policy layer is real and working. The next step should expand that layer rather than fork a separate control surface.

### Decision 2: Keep operator-visible posture and explicit helper surfaces mandatory

Broader policy must remain inspectable through durable-state and user-level helper surfaces.

## Validation Plan

1. Define proposal, design, tasks, and delta specs for broader automatic runtime policies.
2. Extend the Python LangGraph contract and runtime layer with the next bounded policy surface.
3. Expose additive user-level projection and helper surfaces for the richer policy layer.
4. Validate the new posture without regressing current engine, routing, subgraph, or durable-artifact surfaces.
