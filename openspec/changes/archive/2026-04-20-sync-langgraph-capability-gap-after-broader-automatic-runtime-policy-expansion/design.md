## Context

The current repository state has advanced again: the broader automatic runtime-policy mainline is now implemented, validated, and archived. The implementation plan appendix and startup-facing summaries need another sync so they do not continue to frame that runtime-policy step as future work or current implementation work.

## Goals / Non-Goals

**Goals:**

- align the bilingual implementation plan with the current validated LangGraph capability surface after the broader automatic-runtime-policy rollout
- keep implemented, usable-but-bounded, and still-in-plan sections semantically accurate
- refresh startup-facing pointers so the repository no longer points at an already archived active mainline

**Non-Goals:**

- adding new LangGraph runtime behavior
- changing durable backend policy
- reopening already accepted runtime contracts

## Decisions

### Decision 1: Reuse the plan-status-sync capability again

This is still a plan-status alignment pass, so it belongs under `codex-user-level-team-mode-plan-status-sync`.

### Decision 2: Keep the narrative conservative after the broader automatic-policy rollout

The sync should move only validated surfaces into current state and keep remaining boundedness explicit.

## Validation Plan

1. Add a plan-status-sync delta spec for the post-broader-automatic-policy alignment pass.
2. Update the bilingual implementation-plan LangGraph capability-gap appendix.
3. Update startup-facing summaries and current-mainline pointers.
4. Run OpenSpec validation and the repository OpenSpec guard.
