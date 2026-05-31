# Change: Implement Worktree Receipt Claim Lifecycle

## Why
Worktree task receipts and branch-matching session claims already classify most feature worktree states, but the active implementation plan also requires a `stale` lifecycle state and fixture coverage for every allowed state. Without that state, a resumed session cannot label abandoned or obsolete local work without incorrectly calling it active, completed, or superseded.

## What Changes
- Add `stale` to the receipt and branch-matching claim lifecycle status contract.
- Add explicit fixture coverage for every allowed lifecycle state.
- Keep completion evidence required only for integration/completion states: `merged-local-main`, `cleaned`, `remote-sync-needed`, and `completed`.
- Document that `stale` and `superseded` are non-completion classification states and do not force immediate cleanup or branch deletion.

## Impact
- Existing active/paused/ready/completed receipts remain compatible.
- Stale residual worktrees can be classified without claiming successful merge or cleanup.
- Remote publication remains out of scope for this local integration package.
