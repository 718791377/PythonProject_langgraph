## 1. Spec Delta Drafting

- [x] 1.1 Add reducer-backed fan-out / fan-in requirements to `langgraph-durable-orchestration-backend`.
- [x] 1.2 Add reducer-aware inspection requirements to `codex-user-level-inspectable-team-state-surface`.
- [x] 1.3 Reference existing loop semantics only where reducer-backed merge state must remain checkpoint-resumable.

## 2. State Contract Definition

- [x] 2.1 Define the first-rollout classification of LangGraph state channels: reducer-merged, single-writer, and leader-owned derived summary.
- [x] 2.2 Define deterministic fan-in expectations for completed, empty, partial, and invalid branch results.
- [x] 2.3 Define how reducer-aware state records identify merge channels and branch-contributed items.

## 3. Inspection and Compatibility

- [x] 3.1 Define reducer-aware projection fields for the canonical inspectable durable-state summary.
- [x] 3.2 Define how pre-reducer durable records are classified during inspection.
- [x] 3.3 Define source-attribution expectations for merged branch state.

## 4. Validation

- [x] 4.1 Validate deterministic reducer merge behavior for a parallel branch flow.
- [x] 4.2 Validate that invalid multi-writer updates to non-reducer fields are surfaced explicitly.
- [x] 4.3 Validate that reducer-aware merged state remains resumable from persisted checkpoints.
- [x] 4.4 Run `openspec validate --all`.
