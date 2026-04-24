## 1. Spec Delta Drafting

- [x] 1.1 Add compiled `StateGraph` invocation-path requirements to `langgraph-durable-orchestration-backend`
- [x] 1.2 Add compiled-invocation inspection requirements to `codex-user-level-inspectable-team-state-surface`
- [x] 1.3 Add additive user-level compiled-invocation entrypoint requirements to `codex-user-level-team-mode-team-entrypoints`
- [x] 1.4 Add the new `codex-user-level-langgraph-compiled-stategraph-invocation-path` capability spec

## 2. Python LangGraph Compiled-Invocation Implementation

- [x] 2.1 Add compiled-invocation identity and execution fields to `contracts.py`
- [x] 2.2 Persist bounded compiled-invocation posture through the LangGraph CLI/runtime layer
- [x] 2.3 Add an inspectable compiled-invocation command or equivalent library surface for user-level tooling

## 3. User-Level Durable-State Surfaces

- [x] 3.1 Extend installer-generated LangGraph helper surfaces with a compiled-invocation inspection entrypoint
- [x] 3.2 Extend canonical durable-state projection with compiled-invocation posture for tracked LangGraph threads
- [x] 3.3 Update generated playbook or quick-reference guidance for the compiled-invocation lane

## 4. Validation

- [x] 4.1 Add or extend Python tests for compiled-invocation posture and compatibility with current durable artifacts
- [x] 4.2 Extend install-surface integration tests for compiled-invocation inspection behavior
- [x] 4.3 Run `openspec validate --all`
- [x] 4.4 Run `python .\\tools\\run_openspec_guard.py --root .`
