## 1. Spec Delta Drafting

- [x] 1.1 Add command-driven control-flow and parent-handoff requirements to `langgraph-durable-orchestration-backend`
- [x] 1.2 Add command-driven transition and parent-handoff inspection requirements to `codex-user-level-inspectable-team-state-surface`
- [x] 1.3 Add command-aware handoff-boundary requirements to `codex-user-level-langgraph-reusable-subgraph-library`
- [x] 1.4 Add the new `codex-user-level-langgraph-command-driven-control-flow` capability spec

## 2. Python LangGraph Contract Implementation

- [x] 2.1 Add stable command-envelope fields, target-scope fields, and parent-handoff metadata to `contracts.py`
- [x] 2.2 Persist command-driven transition posture and parent-handoff attribution through the LangGraph CLI layer
- [x] 2.3 Extend inspect and status surfaces to expose command-driven transition and resume-payload posture

## 3. User-Level Durable-State Surfaces

- [x] 3.1 Extend installer-generated LangGraph contract and durable-state projections with command-driven and parent-handoff fields
- [x] 3.2 Extend canonical durable-state projection with command-driven transition and parent-handoff data for tracked LangGraph threads
- [x] 3.3 Update generated playbook or quick-reference guidance for command-driven LangGraph control flow

## 4. Validation

- [x] 4.1 Add or extend Python tests for command-driven transition metadata and parent-handoff projection
- [x] 4.2 Extend install-surface integration tests for command-driven durable-state inspection behavior
- [x] 4.3 Run `openspec validate --all`
- [x] 4.4 Run `python .\\tools\\run_openspec_guard.py --root .`
