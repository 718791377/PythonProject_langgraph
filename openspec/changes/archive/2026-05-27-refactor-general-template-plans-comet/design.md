# Design

## Context
The two target documents are implementation plans, not runtime state. They should be sufficient for a future cold-start Codex session to implement or review template changes without copying chat history.

## Decisions
1. Keep `PythonProject_General` and `PythonProject_General_2` as separate capability tiers.
2. Treat Comet as OpenSpec + Superpowers governance only.
3. Make each plan decision-complete: goal, non-goals, capability map, implementation sequence, validation, acceptance, rollback.
4. Keep current-session facts out of template defaults.
5. Promote reusable plan-governance requirements into a stable OpenSpec spec.

## Rollback
Revert the local Git commit. If target template directories were later changed using these plans, revert those target repos independently through their local Git histories.
