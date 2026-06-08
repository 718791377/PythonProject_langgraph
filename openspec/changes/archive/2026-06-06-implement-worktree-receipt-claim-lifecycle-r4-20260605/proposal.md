# Change: Implement Worktree Receipt Claim Lifecycle R4

## Problem

The repository already validates worktree task receipt and branch-matching claim lifecycle labels, but runtime advancement is still manual and fragmented. `tools/complete_local_flow_to_remote_gate.py` records local-main completion, and `tools/cleanup_integrated_worktree.py` preserves cleanup evidence, but there is no shared helper that advances `active`, `ready-to-merge`, `merged-local-main`, `completed`, `cleaned`, `paused`, `superseded`, or `stale` with a consistent transition ledger.

## Goals

- Add a dedicated lifecycle advancement helper for worktree receipts and branch-matching claims.
- Require every transition to record owner, previous state, next state, timestamp, evidence paths, rollback ref when applicable, and cleanup decision.
- Keep remote publication unauthorized by default.
- Integrate local-main completion and safe cleanup flows with the shared transition evidence.
- Update the implementation plan pair and stable spec so cold-start sessions can identify R4 behavior.

## Scope

- `tools/advance_worktree_task_lifecycle.py` - new helper for lifecycle state transitions.
- `tools/complete_local_flow_to_remote_gate.py` - record local-main completion through the shared transition helper.
- `tools/cleanup_integrated_worktree.py` - normalize cleaned lifecycle evidence after safe cleanup.
- Tests covering normal and exceptional transitions.
- OpenSpec delta for multi-session worktree isolation lifecycle advancement.

## Non-goals

- No GitLab/GitHub mutation.
- No remote publication or mirror sync.
- No force deletion of branches, remote refs, backup refs, or unknown dirty work.
- No durable team launch.

## Validation

- Focused lifecycle helper tests.
- Existing worktree receipt, complete-flow, cleanup, ROB, and local-flow tests.
- Repository pre-commit update/archive review.
- OpenSpec guard and local CI gate.
