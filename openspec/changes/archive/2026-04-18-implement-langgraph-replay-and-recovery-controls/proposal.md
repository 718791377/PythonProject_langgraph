## Why

The user-level LangGraph durable lane already supports explicit backend selection, repo-local durable state, checkpointed resume, frozen implementation briefs, persisted survivor queues, quality-gated loops, and reducer-aware merge semantics. What it still lacks is the operator-facing replay and recovery layer that makes durable state auditable and repairable instead of only resumable.

Today the operator can inspect current LangGraph thread posture and resume where appropriate, but cannot cleanly:

- inspect state history as a first-class timeline
- replay prior thread state or checkpoint slices in a read-oriented way
- time-travel to a prior checkpoint with explicit operator intent
- apply explicit recovery mutations such as update-state-style corrections through a bounded user-level control surface

This change closes that gap for the user-level LangGraph durable lane only.

## What Changes

- Define read-oriented replay, checkpoint-history, and state-history inspection for tracked LangGraph durable threads.
- Define explicit recovery controls for the user-level LangGraph lane, including bounded time-travel and update-state-style recovery mutations.
- Define how replay and recovery controls appear in the canonical inspectable durable-state surface and generated user-level entrypoints.
- Keep backend selection, activation policy, quality-gated loops, durable artifacts, and reducer semantics unchanged except where replay or recovery must reference them.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: add replay, time-travel, state-history inspection, and explicit recovery or update-state control semantics for tracked LangGraph threads
- `codex-user-level-inspectable-team-state-surface`: expose replay or history and recovery helper pointers for tracked LangGraph durable state
- `codex-user-level-team-mode-controls`: expose explicit LangGraph replay or recovery control surfaces while keeping mutation explicit
- `codex-user-level-team-mode-team-entrypoints`: add additive LangGraph replay, history, and recovery entrypoints plus playbook guidance

## Impact

- impact_scope:
  - user-level LangGraph durable thread state under `.omx/state/langgraph/`
  - operator-facing replay, history inspection, and bounded recovery helpers
  - canonical inspectable durable-state projections and helper pointers
- explicit_non_goals:
  - no backend-family selection changes
  - no activation-threshold or retrofit-policy changes
  - no reopening of quality-gated loop semantics
  - no redesign of durable artifact types such as frozen briefs or survivor queues
  - no redefinition of reducer merge contracts except where replay or recovery reads or repairs reducer-aware state
- rollout_sequence:
  - define proposal, design, and delta spec contracts for LangGraph replay, history, and recovery controls
  - define read-only replay and state-history inspection semantics
  - define explicit mutation-gated recovery controls for time-travel and update-state-style repair
  - extend inspectable state and entrypoints with replay or recovery helper pointers
  - validate history inspection, replay attribution, bounded recovery mutation, and checkpoint-safe recovery
- rollback_plan:
  - keep replay and recovery controls additive and LangGraph-scoped
  - if recovery mutation proves unsafe, keep read-only replay and history inspection while disabling mutating recovery helpers
  - do not change backend selectors, routing defaults, or startup policy as part of rollback
- validation_path:
  - run `openspec validate --all`
  - validate that history inspection remains read-oriented and source-attributed
  - validate that replay and time-travel target explicit checkpoint or state-history references
  - validate that update-state-style recovery requires explicit operator mutation intent
  - validate that repaired threads remain inspectable and resumable afterward
- mainline_classification:
  - existing mainline continuation
  - specifically a user-level LangGraph replay and recovery-controls step under the Codex / oh-my-codex durable lane
