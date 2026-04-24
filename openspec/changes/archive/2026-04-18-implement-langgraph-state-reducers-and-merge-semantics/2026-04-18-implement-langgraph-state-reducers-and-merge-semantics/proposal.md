## Why

The user-level LangGraph durable lane already has additive backend selection, repo-local thread state, frozen implementation briefs, survivor queues, and first-rollout quality-gated loops. What it still lacks is the reducer-backed merge contract that makes graph-shaped parallel fan-out and deterministic fan-in a real LangGraph capability instead of a mostly sequential durable wrapper.

Without explicit reducer semantics, parallel branch outputs risk drifting into ad hoc overwrite behavior, ambiguous append behavior, or backend-specific merge code that is not inspectable from the durable-state surface.

This change closes that gap for the user-level LangGraph durable lane only.

## What Changes

- Define reducer-backed state channels for user-level LangGraph fan-out / fan-in flows.
- Define which state fields are single-writer overwrite fields versus reducer-merged fields.
- Define deterministic fan-in behavior for parallel branch completion, including empty-branch and partial-branch cases.
- Define reducer-aware inspectable state projection for LangGraph durable threads.
- Keep existing backend selection, activation policy, and quality-gated loop policy unchanged except where reducer-backed state must coexist with those already-defined behaviors.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: add reducer-backed fan-out / fan-in state merge semantics for the user-level LangGraph durable lane
- `codex-user-level-inspectable-team-state-surface`: expose reducer-aware LangGraph merge status and source attribution through inspectable projection fields

## Impact

- impact_scope:
  - user-level LangGraph durable thread state under `.omx/state/langgraph/`
  - reducer-aware fan-out / fan-in state contracts
  - read-oriented operator inspection of merged branch state
- explicit_non_goals:
  - no backend-family selection changes
  - no activation-threshold or retrofit-policy changes
  - no new default routing to `langgraph`
  - no replay, time-travel, or reusable-subgraph scope
  - no reopening of loop-family policy beyond reducer compatibility
- rollout_sequence:
  - define proposal, design, and spec contracts for reducer-backed fan-out / fan-in semantics
  - classify LangGraph state channels into reducer-merged, single-writer, and leader-owned summary classes
  - add reducer-aware merge metadata to persisted LangGraph state and inspectable projections
  - validate deterministic merge behavior, invalid multi-writer protection, and checkpoint-safe resume
- rollback_plan:
  - keep reducer semantics additive and scoped to explicitly declared merge channels
  - if reducer-aware merge state proves unstable, preserve existing branch execution while disabling reducer-specific merge handling and projection
  - do not change backend selectors, startup mode, or routing defaults as part of rollback
- validation_path:
  - run `openspec validate --all`
  - validate that reducer-declared fields merge deterministically across parallel branches
  - validate that non-reducer fields do not silently multi-writer merge
  - validate that fan-in state is resumable from persisted checkpoints
  - validate that inspectable state exposes reducer-aware merge status and source attribution
- mainline_classification:
  - existing mainline continuation
  - specifically a user-level LangGraph reducer and merge-semantics step under the Codex / oh-my-codex team-mode line
