## 1. Spec Delta Drafting

- [x] 1.1 Add replay, checkpoint-history, and state-history inspection requirements to `langgraph-durable-orchestration-backend`.
- [x] 1.2 Add explicit recovery and update-state-style mutation requirements to `langgraph-durable-orchestration-backend`.
- [x] 1.3 Extend `codex-user-level-inspectable-team-state-surface` with replay or recovery posture and helper-pointer requirements.
- [x] 1.4 Extend `codex-user-level-team-mode-controls` and `codex-user-level-team-mode-team-entrypoints` with additive LangGraph replay, history, and recovery control requirements.

## 2. Replay and History Contract

- [x] 2.1 Define the minimum replay and history inspection fields for tracked LangGraph threads.
- [x] 2.2 Define stable target identity for checkpoint or state-history replay views.
- [x] 2.3 Define compatibility behavior for older records with reduced history metadata.

## 3. Recovery Control Contract

- [x] 3.1 Define explicit time-travel targeting and mutation gating.
- [x] 3.2 Define first-rollout update-state-style recovery boundaries and recoverable-field classes.
- [x] 3.3 Define how recovery actions preserve existing interrupt, checkpoint, durable-artifact, and reducer-aware semantics.

## 4. Inspectability and Entry Surfaces

- [x] 4.1 Define canonical durable-state projection fields for replay and recovery posture.
- [x] 4.2 Define helper pointers for LangGraph replay, history inspect, time-travel, and update-state-style recovery.
- [x] 4.3 Define how read-only inspection is distinguished from explicit mutation controls in generated assets.

## 5. Validation

- [x] 5.1 Validate that replay and state-history inspection remain read-oriented and source-attributed.
- [x] 5.2 Validate that time-travel requires an explicit historical target and does not occur implicitly.
- [x] 5.3 Validate that update-state-style recovery rejects out-of-scope or invalid state mutation attempts.
- [x] 5.4 Validate that recovered LangGraph state remains inspectable and resumable afterward.
- [x] 5.5 Run `openspec validate --all`.
