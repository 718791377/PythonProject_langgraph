## 1. Spec Delta Drafting

- [x] 1.1 Add streaming and debug observability requirements to `langgraph-durable-orchestration-backend`
- [x] 1.2 Add streaming-posture inspection requirements to `codex-user-level-inspectable-team-state-surface`
- [x] 1.3 Add additive stream-observability entrypoint requirements to `codex-user-level-team-mode-team-entrypoints`
- [x] 1.4 Add the new `codex-user-level-langgraph-streaming-and-debug-observability-surface` capability spec

## 2. Python LangGraph Observability Implementation

- [x] 2.1 Add stream-mode, nested-subgraph, and latest-event contract fields to `contracts.py`
- [x] 2.2 Persist stream-session posture and bounded latest-event summaries through the LangGraph CLI layer
- [x] 2.3 Add an inspectable stream-observability command or equivalent library surface for user-level tooling

## 3. User-Level Durable-State Surfaces

- [x] 3.1 Extend installer-generated LangGraph helper surfaces with a stream-observability entrypoint
- [x] 3.2 Extend canonical durable-state projection with streaming posture and latest-event data for tracked LangGraph threads
- [x] 3.3 Update generated playbook or quick-reference guidance for LangGraph streaming and debug observability

## 4. Validation

- [x] 4.1 Add or extend Python tests for streaming-mode metadata, debug-event projection, and nested subgraph visibility
- [x] 4.2 Extend install-surface integration tests for stream-observability inspection behavior
- [x] 4.3 Run `openspec validate --all`
- [x] 4.4 Run `python .\\tools\\run_openspec_guard.py --root .`
