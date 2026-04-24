## 1. Spec Delta Drafting

- [x] 1.1 Add reusable subgraph-library requirements to `langgraph-durable-orchestration-backend`
- [x] 1.2 Add active-subgraph and subgraph-library inspection requirements to `codex-user-level-inspectable-team-state-surface`
- [x] 1.3 Add additive LangGraph subgraph-library entrypoint requirements to `codex-user-level-team-mode-team-entrypoints`
- [x] 1.4 Add the new `codex-user-level-langgraph-reusable-subgraph-library` capability spec

## 2. Python LangGraph Library Implementation

- [x] 2.1 Replace the shallow `SUBGRAPHS` map with a richer reusable subgraph-library contract in `contracts.py`
- [x] 2.2 Persist active-subgraph metadata and subgraph-aware projections through the LangGraph CLI layer
- [x] 2.3 Add an inspectable subgraph-library command or equivalent library surface for user-level tooling

## 3. User-Level Entry Surfaces

- [x] 3.1 Extend installer-generated LangGraph helper surfaces with a reusable subgraph-library inspection entrypoint
- [x] 3.2 Extend canonical durable-state projection with active-subgraph and subgraph-library data for tracked LangGraph threads
- [x] 3.3 Update generated playbook or quick-reference guidance for the new subgraph-library surface

## 4. Validation

- [x] 4.1 Add or extend Python tests for reusable subgraph contracts and active-subgraph projection
- [x] 4.2 Extend install-surface integration tests for the new entrypoint and inspection behavior
- [x] 4.3 Run `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
- [x] 4.4 Run `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
- [x] 4.5 Run `openspec validate --all`
- [x] 4.6 Run `python .\\tools\\run_openspec_guard.py --root .`
