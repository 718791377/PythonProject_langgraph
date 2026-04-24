## Why

The bilingual Codex / oh-my-codex user-level team-mode implementation plan has become partially stale relative to the currently implemented control surfaces, LangGraph backend integration, and archived P0-P7 capability batches. This now risks confusing operators because the plan still mixes implemented, optional, future, and already-landed behavior in ways that no longer match the real user-level installation and runtime.

## What Changes

- Audit the canonical bilingual team-mode implementation plan against the current user-level installer outputs, main specs, and archived change history.
- Update stale status markers, especially where the plan still labels already-landed capabilities as planned or future.
- Reconcile the P0-P7 mapping table and surrounding narrative with current implementation reality.
- Clarify which surfaces are implemented now, which remain optional advanced paths, and which are still truly future.
- Keep the English and Chinese plan files semantically aligned after the sync.

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-plan-status-sync`: keep the canonical bilingual team-mode implementation plan aligned with current implemented state, optional advanced paths, and future work boundaries

### Modified Capabilities
- `documentation-layering-and-bilingual-openspec-governance`: clarify how canonical implementation-plan documents should distinguish implemented state from future state for active user-level team-mode surfaces

## Impact

- impact_scope:
  - bilingual implementation-plan documents for Codex / oh-my-codex user-level team mode
  - documentation governance for how current state vs future state is expressed
  - operator understanding of what is already usable
- explicit_non_goals:
  - no runtime behavior change by itself
  - no installer or wrapper implementation changes unless drift is found while syncing
  - no new durable backend
- rollout_sequence:
  - compare current plan documents to implemented surfaces and main specs
  - update stale sections, phase tables, and operator guidance
  - validate bilingual semantic alignment
- rollback_plan:
  - revert only the synced documentation and any documentation-only spec changes
  - preserve runtime and installer behavior unchanged
- validation_path:
  - confirm the plan reflects current user-level assets and state files
  - confirm the plan distinguishes implemented vs optional vs future correctly
  - run `openspec validate --all`
- mainline_classification:
  - existing mainline continuation
  - specifically a documentation-state synchronization pass for the Codex / oh-my-codex user-level team-mode line
