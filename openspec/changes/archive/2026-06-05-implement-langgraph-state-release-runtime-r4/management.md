# Management Checklist

## Open

- [x] Value and why recorded: runtime release helper closes the gap left by checker-only evidence.
- [x] Success criteria recorded: release receipt, non-running thread status, projection evidence, and tests.
- [x] Constraints recorded: local-only implementation and no remote publication authorization.

## Design

- [x] Delivery tailoring recorded: one serialized R4 runtime slice in an isolated worktree.
- [x] Risks and assumptions recorded: no automatic backend-family switch and no artifact deletion.
- [x] Acceptance evidence path recorded: targeted runtime tests, checker tests, OpenSpec guard, local gate, and local MR review.

## Build

- [x] Execution mode recorded: executing-plans in isolated worktree with TDD.
- [x] Quality evidence recorded: failing-first runtime test failed on missing `release-thread`; runtime helper coverage now lives in the existing CI-managed state-release test module and passes with the checker tests.
- [x] Blocker decision recorded: none during build; CLI entrypoint mismatch was resolved by syncing both top-level and package helper copies.

## Verify

- [x] Variance review recorded: implementation covers receipt path, close/release/handoff actions, required handoff fields, non-running terminal status, and status/inspect/backend projections.
- [x] Risk/change impact recorded in design and proposal.
- [x] Control decision: continue to archive after OpenSpec guard passes.

## Archive

- [x] Value outcome will be summarized by archive and stable spec promotion.
- [x] Lessons learned will remain in the stable backend spec, not only in chat.
- [x] Archive/sync evidence captured: archived at `openspec/changes/archive/2026-06-05-implement-langgraph-state-release-runtime-r4/` and promoted into `openspec/specs/langgraph-durable-orchestration-backend/spec.md` before local main integration.

## Monitoring

- [x] Current facts checked: single execution slice and active worktree claim.
- [x] Return/no-return decision: continue.
