## Why

The canonical bilingual Codex / oh-my-codex user-level team-mode plan has drifted behind the current implemented user-level state. It still leaves some already-landed control surfaces, layered capability behavior, and user-level operator guidance described as future direction, which now conflicts with the real user-level installation under `C:\Users\lenovo\.codex`.

## What Changes

- Reclassify already-landed user-level team-mode behavior in the canonical bilingual plan from future direction to implemented current state where the behavior is already installed and validated.
- Remove or rewrite plan wording that still describes layered capability switches, per-task effective-lane choice, and current user-level operator surfaces as not yet landed when they are already present in the user-level installation.
- Align the bilingual plan with the current user-level operator-facing surfaces for routing policy, backend selection, leader protocol, and global provider-pacing interpretation.
- Preserve a clean boundary between:
  - implemented current state
  - optional advanced paths
  - true future work
- Keep true future directions, such as later optional compose-layer work, explicitly marked as future rather than letting current-state and future-state language blur together.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `codex-user-level-team-mode-plan-status-sync`: tighten the canonical bilingual plan-sync contract so the implementation plan reflects the current installed user-level state, current operator-facing interpretation, and true future-work boundaries without leaving already-landed behavior mislabeled as future.

## Impact

- impact_scope:
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md`
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md`
  - delta spec updates for plan-status sync
  - change artifacts for documenting the corrected current-state vs future-state boundary
- explicit_non_goals:
  - no new orchestration backend
  - no new durable-team runtime behavior
  - no new mixed-pane compose implementation
  - no repository-specific LangGraph migration plan
  - no change to current user-level global switch values
- rollout_sequence:
  - compare the bilingual plan against the current installed user-level surfaces and validated behavior
  - identify mismatches where already-landed behavior is still described as future or ambiguous
  - update the canonical bilingual plan to reflect implemented current state, optional advanced paths, and true future work consistently
  - validate semantic alignment between the English and Chinese plan files
- rollback_plan:
  - revert the bilingual plan files and the delta spec if the reclassification proves incorrect
  - restore the previous document state from version control if the updated classification causes policy confusion
- validation_path:
  - compare the updated bilingual plan against the real user-level operator-facing surfaces under `C:\Users\lenovo\.codex`
  - confirm that already-landed layered capability, effective-lane, and provider-pacing guidance is no longer mislabeled as future work
  - run `openspec validate --all`
- mainline_classification:
  - existing mainline continuation
  - specifically a user-level team-mode plan/status synchronization pass
