## 1. Spec Delta Drafting

- [x] 1.1 Add reducer-aware live primary-engine merge-state requirements to `langgraph-durable-orchestration-backend`
- [x] 1.2 Add reducer-aware live-engine inspection requirements to `codex-user-level-inspectable-team-state-surface`
- [x] 1.3 Add additive user-level reducer-aware live-engine entrypoint requirements to `codex-user-level-team-mode-team-entrypoints`
- [x] 1.4 Add the new `codex-user-level-langgraph-reducer-aware-live-primary-engine-merge-state` capability spec

## 2. Python LangGraph Engine Implementation

- [x] 2.1 Extend `contracts.py` with reducer-aware live primary-engine identity and projection fields
- [x] 2.2 Implement reducer-aware live primary-engine behavior through the LangGraph CLI/runtime layer
- [x] 2.3 Add an inspectable reducer-aware live primary-engine command or equivalent library surface for user-level tooling

## 3. User-Level Durable-State Surfaces

- [x] 3.1 Extend installer-generated LangGraph helper surfaces with a reducer-aware live-engine inspection entrypoint
- [x] 3.2 Extend canonical durable-state projection with reducer-aware live-engine posture for tracked LangGraph threads
- [x] 3.3 Update generated playbook or quick-reference guidance for the reducer-aware lane

## 4. Validation

- [x] 4.1 Add or extend Python tests for reducer-aware live-engine posture
- [x] 4.2 Extend install-surface integration tests for reducer-aware live-engine inspection behavior
- [x] 4.3 Run `openspec validate --all`
- [x] 4.4 Run `python .\\tools\\run_openspec_guard.py --root .`
