## 1. Spec Delta Drafting

- [x] 1.1 Add memory-store and semantic-memory requirements to `langgraph-durable-orchestration-backend`
- [x] 1.2 Add memory-store and semantic-memory inspection requirements to `codex-user-level-inspectable-team-state-surface`
- [x] 1.3 Add additive memory/store inspection entrypoint requirements to `codex-user-level-team-mode-team-entrypoints`
- [x] 1.4 Add the new `codex-user-level-langgraph-memory-store-and-semantic-memory` capability spec

## 2. Python LangGraph Memory Implementation

- [x] 2.1 Add memory-store and semantic-memory contract fields to `contracts.py`
- [x] 2.2 Persist bounded memory-store and semantic-memory metadata through the LangGraph CLI layer
- [x] 2.3 Add an inspectable memory/store command or equivalent library surface for user-level tooling

## 3. User-Level Durable-State Surfaces

- [x] 3.1 Extend installer-generated LangGraph helper surfaces with a memory/store inspection entrypoint
- [x] 3.2 Extend canonical durable-state projection with memory-store and semantic-memory posture for tracked LangGraph threads
- [x] 3.3 Update generated playbook or quick-reference guidance for memory-store and semantic-memory inspection

## 4. Validation

- [x] 4.1 Add or extend Python tests for memory-store and semantic-memory projection
- [x] 4.2 Extend install-surface integration tests for memory/store inspection behavior
- [x] 4.3 Run `openspec validate --all`
- [x] 4.4 Run `python .\\tools\\run_openspec_guard.py --root .`
