# Design: Legacy Durable Residue Classification

## Decision

Use the existing worktree receipt checker as the first read-only inventory surface because it already runs during local pre-commit and worktree lifecycle validation. The checker now classifies repo-local `.omx/state/` residue as evidence rather than as activation state.

## Classification Model

Each durable residue record includes:

- `kind`: stable machine-readable residue class.
- `path`: repo-relative source path.
- `state_class`: safety grouping for operator handling. Values used in this rollout are:
  - `safe_cleanup_candidate` - empty or stale residue that may be removed only through the approved reconciliation path.
  - `protected_residue` - ambiguous or non-empty residue that requires manual inspection.
  - `stale_selector` - selector evidence that points outside the current repository and should be refreshed or ignored.
  - `selector_authority` - selector evidence for the current repository; it is authority evidence but not adoption permission by itself.
  - `legacy_completed_state` - completed LangGraph state that may be inspected or archived but not auto-resumed.
  - `inspectable_legacy_state` - legacy state that remains evidence until an operator chooses a safe follow-up.
- `safe_next_action`: operator-safe next action.
- `auto_adopt_allowed`: always false for this rollout.
- `reason`: source-attributed explanation.

## Safety Boundaries

- Empty unmanaged native team directories are safe cleanup candidates only through the approved reconciliation path.
- Non-empty unmanaged native team directories are protected residue and require manual inspection.
- Stale selectors are refresh or ignore candidates, not adoption authority.
- Active current selectors are authority evidence but do not by themselves authorize auto-adoption.
- Completed LangGraph state is inspect-or-archive evidence and must not be auto-resumed.

## Alternatives Considered

- Extending the generated PowerShell installer helper first: rejected for this child plan because the local checker provides faster, repository-owned evidence and avoids touching generated user-level helper behavior.
- Mutating `.omx/state/` during classification: rejected because this child plan is classification-only and must remain read-only.
