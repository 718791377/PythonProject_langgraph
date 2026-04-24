## Context

The repository just closed the initial queued LangGraph deepening wave: reusable subgraphs, command-driven handoffs, streaming observability, runtime/store injection, memory posture, graph-migration compatibility, and multi-interrupt approval queues are all now implemented and validated.

The remaining problem is not code behavior. The remaining problem is narrative drift. The bilingual implementation plan still treats some of those surfaces as future work, and the startup-facing summary still frames the sync pass itself as the next pending action.

## Goals / Non-Goals

**Goals:**

- align the bilingual implementation plan with the current validated LangGraph capability surface
- keep “implemented”, “usable but still bounded”, and “still in plan” sections semantically accurate
- remove stale startup-facing wording that says the sync pass is still pending after it has completed

**Non-Goals:**

- adding new LangGraph runtime features
- changing current OpenSpec capability contracts outside plan-status sync
- reworking repository architecture or backend policy

## Decisions

### Decision 1: Modify the plan-status-sync capability instead of inventing a new documentation capability

This work is a plan-status alignment pass, so it should extend the existing `codex-user-level-team-mode-plan-status-sync` contract rather than create a separate documentation-only capability family.

### Decision 2: Keep the LangGraph capability-gap appendix truthful but not maximalist

The sync should not swing from underclaiming to overclaiming. Already-implemented surfaces should move into implemented current state, while genuinely unlanded work should remain in the “still in plan” section.

### Decision 3: Update startup-facing summaries together with the implementation plan

The implementation plan and startup summary should not diverge. Once the sync pass is complete, startup-facing text should stop pointing to the sync pass as an unfinished next step.

## Risks / Trade-offs

- [Risk] The sync may overstate the current LangGraph runtime. -> Mitigation: keep the “still not fully realized” boundary explicit.
- [Risk] English and Chinese files may drift semantically. -> Mitigation: update both appendix sections in the same change.
- [Risk] Startup-facing pointers may become stale immediately after archive. -> Mitigation: update README, AGENTS, and startup summaries in the same pass.

## Validation Plan

1. Add a plan-status-sync delta spec for LangGraph capability-gap alignment.
2. Update the bilingual implementation plan appendix to reflect the current validated surface.
3. Update startup-facing repository summaries to remove stale “sync still pending” wording.
4. Run OpenSpec validation and the repository OpenSpec guard.
