## Why

The repository has now closed the bounded graph-kernel, primary-runtime engine, compiled-invocation, live-execution, generalized live-routing, and subgraph persistence or state-inspection mainlines. The remaining top runtime gap in the synced implementation plan is no longer route identity or reusable-subgraph posture. It is the execution engine itself.

The current user-level LangGraph lane can already project live execution posture, but it still behaves as a bounded compatibility layer around repo-local state. The next justified runtime step is therefore a fuller live `StateGraph` primary execution engine that moves beyond bounded live-execution posture toward richer primary execution semantics while preserving the current operator model.

## What Changes

- Introduce a fuller live `StateGraph` primary execution engine for the user-level LangGraph durable lane.
- Move the current live-execution layer from bounded execution posture toward richer primary execution semantics while staying compatibility-aware.
- Preserve the seven-phase operator shell, durable artifacts, and inspectable user-level surfaces during the rollout.
- Keep the result additive to the current Codex leader model and the existing LangGraph runtime layers.

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-fuller-live-stategraph-primary-execution-engine`: richer live primary execution semantics for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: extend live execution from bounded posture toward a fuller primary execution engine
- `codex-user-level-inspectable-team-state-surface`: expose fuller live primary-engine execution posture without breaking the canonical durable-state summary
- `codex-user-level-team-mode-team-entrypoints`: expose additive user-level inspection helpers for the fuller live primary-engine lane

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` live-engine projection data
  - LangGraph Python tests and install-surface integration tests
- explicit_non_goals:
  - this change does not replace the current Codex CLI leader model
  - this change does not replace `native_omx` as the worker-centric default backend
  - this change does not attempt to land every future LangGraph automation policy in one pass
  - this change does not require cloud-only orchestration infrastructure
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for fuller primary-engine execution posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
