# Design: Worktree Receipt Claim Lifecycle

## Decisions
- Use one shared lifecycle vocabulary for worktree receipts and branch-matching claim labels in `tools/check_worktree_task_receipt.py`.
- Treat `stale` as a classification state, not a completion state. It records abandoned, obsolete, or no-longer-current local work while preserving the next-action field for operator triage.
- Keep completion evidence mandatory only for states that assert local-main integration or cleanup progress: `merged-local-main`, `cleaned`, `remote-sync-needed`, and `completed`.
- Avoid changing the broader implementation-plan claim-lock checker in this package because another active local claim currently owns that checker surface. This change only validates branch-matching claims through the worktree receipt checker.

## Validation
- Fixture coverage must equal the allowed lifecycle-state set.
- Focused tests must prove stale receipt and stale claim labels are accepted without completion fields.
- Focused tests must prove integration/completion states still fail without completion evidence.
