## 1. Spec Delta Drafting

- [x] 1.1 Add `StateGraph` runtime-kernel requirements to `langgraph-durable-orchestration-backend`
- [x] 1.2 Add kernel-aware graph-state inspection requirements to `codex-user-level-inspectable-team-state-surface`
- [x] 1.3 Add additive user-level runtime-kernel entrypoint requirements to `codex-user-level-team-mode-team-entrypoints`
- [x] 1.4 Add the new `codex-user-level-langgraph-stategraph-runtime-kernel` capability spec

## 2. Python LangGraph Runtime-Kernel Implementation

- [x] 2.1 Add graph-kernel identity and phase-to-node mapping fields to `contracts.py`
- [x] 2.2 Persist bounded graph-native kernel posture through the LangGraph CLI/runtime layer
- [x] 2.3 Add an inspectable graph-kernel command or equivalent library surface for user-level tooling

## 3. User-Level Durable-State Surfaces

- [x] 3.1 Extend installer-generated LangGraph helper surfaces with a graph-kernel inspection entrypoint
- [x] 3.2 Extend canonical durable-state projection with graph-kernel posture for tracked LangGraph threads
- [x] 3.3 Update generated playbook or quick-reference guidance for the `StateGraph` runtime-kernel lane

## 4. Validation

- [x] 4.1 Add or extend Python tests for graph-kernel posture and compatibility with current durable artifacts
- [x] 4.2 Extend install-surface integration tests for graph-kernel inspection behavior
- [x] 4.3 Run `openspec validate --all`
- [x] 4.4 Run `python .\\tools\\run_openspec_guard.py --root .`
