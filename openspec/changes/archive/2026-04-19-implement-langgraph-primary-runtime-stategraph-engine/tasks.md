## 1. Spec Delta Drafting

- [x] 1.1 Add primary-runtime `StateGraph` engine requirements to `langgraph-durable-orchestration-backend`
- [x] 1.2 Add engine-aware graph-state inspection requirements to `codex-user-level-inspectable-team-state-surface`
- [x] 1.3 Add additive user-level primary-runtime entrypoint requirements to `codex-user-level-team-mode-team-entrypoints`
- [x] 1.4 Add the new `codex-user-level-langgraph-primary-runtime-stategraph-engine` capability spec

## 2. Python LangGraph Primary-Runtime Implementation

- [x] 2.1 Add primary-runtime engine identity and compiled-graph execution fields to `contracts.py`
- [x] 2.2 Persist bounded primary-runtime engine posture through the LangGraph CLI/runtime layer
- [x] 2.3 Add an inspectable primary-runtime engine command or equivalent library surface for user-level tooling

## 3. User-Level Durable-State Surfaces

- [x] 3.1 Extend installer-generated LangGraph helper surfaces with a primary-runtime engine inspection entrypoint
- [x] 3.2 Extend canonical durable-state projection with primary-runtime engine posture for tracked LangGraph threads
- [x] 3.3 Update generated playbook or quick-reference guidance for the primary-runtime engine lane

## 4. Validation

- [x] 4.1 Add or extend Python tests for primary-runtime engine posture and compatibility with current durable artifacts
- [x] 4.2 Extend install-surface integration tests for primary-runtime engine inspection behavior
- [x] 4.3 Run `openspec validate --all`
- [x] 4.4 Run `python .\\tools\\run_openspec_guard.py --root .`
