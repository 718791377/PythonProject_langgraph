## Context

The current repository state has advanced again: generalized live-routing is now implemented, validated, and archived; subgraph persistence modes and bounded subgraph-state inspection are also now implemented, validated, and archived.

The plan-layer narrative has not caught up yet. The implementation plan appendix and startup-facing summaries need a fresh sync so that they do not continue to treat those surfaces as active gaps.

## Goals / Non-Goals

**Goals:**

- align the bilingual implementation plan with the current validated LangGraph capability surface after the subgraph-persistence rollout
- keep implemented, usable-but-bounded, and still-in-plan sections semantically accurate
- refresh startup-facing pointers so the repository no longer points to an already archived active mainline

**Non-Goals:**

- adding new LangGraph runtime behavior
- changing durable backend policy
- reopening already accepted runtime contracts

## Decisions

### Decision 1: Reuse the plan-status-sync capability instead of inventing a new documentation-only capability

This is still a plan-status alignment pass, so it should extend the existing `codex-user-level-team-mode-plan-status-sync` capability family.

### Decision 2: Keep the narrative conservative

The sync should move only validated surfaces into current state. It should keep boundedness and remaining runtime limits explicit instead of swinging into overclaiming.

### Decision 3: Update startup-facing summaries in the same pass

The implementation plan, README, AGENTS, and bilingual startup summaries should move together. Otherwise the repository immediately re-enters drift.

## Validation Plan

1. Add a plan-status-sync delta spec for the post-subgraph-persistence alignment pass.
2. Update the bilingual implementation-plan LangGraph capability-gap appendix.
3. Update startup-facing summaries and current-mainline pointers.
4. Run OpenSpec validation and the repository OpenSpec guard.
