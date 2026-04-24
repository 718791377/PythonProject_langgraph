## 1. Spec Delta Drafting

- [x] 1.1 Add subgraph persistence-mode requirements to `langgraph-durable-orchestration-backend`
- [x] 1.2 Add subgraph persistence and inspection projection requirements to `codex-user-level-inspectable-team-state-surface`
- [x] 1.3 Add additive user-level subgraph-state inspection entrypoint requirements to `codex-user-level-team-mode-team-entrypoints`
- [x] 1.4 Add the new `codex-user-level-langgraph-subgraph-persistence-modes-and-state-inspection` capability spec

## 2. Python LangGraph Subgraph Persistence Implementation

- [x] 2.1 Add subgraph persistence-mode and inspection fields to `contracts.py`
- [x] 2.2 Persist bounded subgraph persistence and inspection posture through the LangGraph CLI/runtime layer
- [x] 2.3 Add an inspectable subgraph-state command or equivalent library surface for user-level tooling

## 3. User-Level Durable-State Surfaces

- [x] 3.1 Extend installer-generated LangGraph helper surfaces with a subgraph-state inspection entrypoint
- [x] 3.2 Extend canonical durable-state projection with subgraph persistence-mode and inspection posture for tracked LangGraph threads
- [x] 3.3 Update generated playbook or quick-reference guidance for the subgraph persistence lane

## 4. Validation

- [x] 4.1 Add or extend Python tests for subgraph persistence-mode and state-inspection posture
- [x] 4.2 Extend install-surface integration tests for subgraph-state inspection behavior
- [x] 4.3 Run `openspec validate --all`
- [x] 4.4 Run `python .\\tools\\run_openspec_guard.py --root .`
