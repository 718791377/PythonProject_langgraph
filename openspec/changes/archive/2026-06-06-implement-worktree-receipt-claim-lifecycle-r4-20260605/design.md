# Design: Worktree Receipt Claim Lifecycle R4

## Overview

Add `tools/advance_worktree_task_lifecycle.py` as the single runtime helper for receipt and claim lifecycle advancement. The helper updates both local-only metadata surfaces when present:

- `.omx/worktree-task-receipt.json` inside the feature worktree.
- `.omx/session-claims/<session>.json` branch-matching claim inside that same worktree.

The helper appends a `lifecycle_transitions` ledger entry on every state change. It does not mutate remotes and does not merge local main by itself.

## Transition model

Allowed next states reuse the existing receipt/claim lifecycle vocabulary:

- `active` - the worktree is currently owned and writable for the task.
- `paused` - the owner intentionally stopped before merge and left a resume reason.
- `ready-to-merge` - local validation has completed and the package can enter local-main integration.
- `merged-local-main` - local `main` contains the feature branch result and rollback evidence exists.
- `completed` - local package evidence is complete while remote publication remains separately gated.
- `cleaned` - guarded cleanup removed the local worktree and deleted the merged local branch.
- `remote-sync-needed` - local completion needs later explicitly authorized remote publication or mirror sync.
- `superseded` - another package replaces this work before local-main integration.
- `stale` - residual work is classified as obsolete without claiming merge or cleanup.

The helper is fail-closed for invalid order. Normal forward transitions are:

1. `active` or `paused` to `ready-to-merge`
2. `ready-to-merge` to `merged-local-main`
3. `merged-local-main` or `completed` to `cleaned`

Exceptional transitions from `active`, `paused`, or `ready-to-merge` may go to `paused`, `superseded`, or `stale` when a reason is recorded.

## Evidence fields

Each transition records:

- `transitioned_at` - timestamp for when the lifecycle transition was recorded.
- `owner` - helper or session that recorded the lifecycle transition.
- `previous_state` - lifecycle state before the transition.
- `next_state` - lifecycle state after the transition.
- `evidence_paths` - lightweight paths or command labels that support the transition.
- `rollback_ref` - local backup ref used to restore the pre-merge mainline if needed.
- `local_main_commit` - local `main` commit that contains the integrated package.
- `cleanup_decision` - defines whether cleanup is preserved, deferred, or executed for this transition.
- `reason` - human-readable explanation for exceptional or operator-driven transitions.
- `remote_publication_authorized=false` - explicit marker that remote mutation is still blocked.

Integration/completion states also preserve completion fields required by the existing checker:

- `completed_at` - timestamp for integration or cleanup completion evidence.
- `rollback_ref` - local backup ref used to restore the pre-merge mainline if needed.
- `local_main_commit` - local `main` commit that contains the integrated package.
- `cleaned_worktree` - path or status describing the worktree cleanup result.
- `deleted_branch` - local branch deletion evidence or preservation status.
- `remote_sync_status` - defines whether GitLab/GitHub publication is blocked, pending, or completed.

## Integration points

`tools/complete_local_flow_to_remote_gate.py` records the `merged-local-main` transition after the local fast-forward merge and post-merge local gate.

`tools/cleanup_integrated_worktree.py` records or normalizes the `cleaned` transition after it removes the worktree and deletes the merged local feature branch. The preserved completed claim under the primary root carries the cleaned lifecycle evidence.

## Safety

The helper refuses to advance integration states without rollback and local-main evidence. Cleanup states require cleanup evidence. Remote publication remains closed unless a future explicitly authorized remote flow updates separate remote evidence.
