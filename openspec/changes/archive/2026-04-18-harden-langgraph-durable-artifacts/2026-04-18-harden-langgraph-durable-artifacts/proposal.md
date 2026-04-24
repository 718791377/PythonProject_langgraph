## Why

The current user-level bilingual plan already treats LangGraph as the preferred additive backend when work depends on graph phases, checkpoint gates, frozen implementation briefs, or persisted survivor queues. Repo-local LangGraph state and backend-aware entrypoints already exist, but the artifact contract for `frozen implementation brief` and `survivor queue` is still too loose. That leaves room for drift between what the user-level plan says should exist, what LangGraph thread state exposes, and what operator-facing inspection surfaces can reliably show.

This change hardens those two durable artifacts without reopening backend-selection policy, activation policy, or the additive-versus-default LangGraph decision.

## What Changes

- Formalize the artifact shape and minimum fields for the frozen implementation brief.
- Formalize the artifact shape and minimum fields for the survivor queue.
- Define persistence and inspectability rules for both artifacts in tracked LangGraph durable state.
- Define canonical operator-facing visibility of artifact presence, status, and pointers.
- Keep LangGraph additive, keep one durable task within one backend family, and keep existing routing and activation policies unchanged.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: harden research handoff and adversarial-review outputs into stable, inspectable durable artifacts
- `codex-user-level-inspectable-team-state-surface`: expose LangGraph durable artifact presence and pointers explicitly without reopening backend-selection policy

## Impact

- impact_scope:
  - artifact contracts inside repo-local LangGraph durable state under `.omx/state/langgraph/`
  - operator-facing inspection of brief and survivor-queue presence
  - documentation and implementation alignment for user-level LangGraph durable artifacts
- explicit_non_goals:
  - no backend-selection policy changes
  - no activation or re-check policy changes
  - no change to whether LangGraph is additive versus default
  - no requirement that native durable-team adopt the same artifact storage model
  - no reducer, replay, or reusable-subgraph scope in this change
- rollout_sequence:
  - define proposal, design, and delta spec contracts for hardened durable artifacts
  - specify stable minimum fields and lifecycle rules for the frozen brief and survivor queue
  - extend inspectable state surfaces with artifact presence and pointer guidance
  - validate artifact persistence and fresh-context or repair-lane consumption
- rollback_plan:
  - keep the current additive LangGraph backend model intact
  - if hardened artifact semantics prove incomplete, preserve the existing weaker artifact behavior while removing the new strict presence and status expectations
  - do not change backend selectors, startup mode, or routing defaults as part of rollback
- validation_path:
  - run `openspec validate --all`
  - validate that research handoff persists a stable frozen brief before implementation continues
  - validate that adversarial review persists only judged survivors into a resumable repair queue
  - validate that inspectable state surfaces expose artifact presence and pointers without requiring backend-specific file inference
- mainline_classification:
  - existing mainline continuation
  - specifically a user-level LangGraph durable-artifact hardening step under the Codex / oh-my-codex team-mode line
