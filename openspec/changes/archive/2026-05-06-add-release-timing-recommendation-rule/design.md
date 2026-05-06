# Design: Release timing recommendation rule

## Decision Boundary

The active session's model should recommend release timing because it has the current local context: validation results, active OpenSpec state, review scope, rollback boundary, and runner-budget value.

The user remains the release decision authority. The model recommends; the user confirms.

## Recommendation Inputs

The recommendation should consider:

- local validation state
- active-change state
- review scope
- rollback boundary
- runner-budget value
- whether additional same-topic changes are likely to arrive immediately

## Placement

The rule belongs in startup and publication governance surfaces so cold-start sessions know to advise before pushing.
