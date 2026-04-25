## Why

The repository has now closed the stateful live primary-engine mainline and the follow-up capability-gap sync pass. The most concrete remaining runtime gap is no longer graph-carried next-hop state alone; it is the boundary state of the live primary engine itself.

The current `stateful-engine` lane can carry next-hop decisions and transition logs inside graph-native execution state. But interrupt, recovery, and terminal boundary handling are still short-circuited outside the compiled graph before graph-native execution begins.

The next justified mainline is therefore a graph-resident live primary-engine boundary-state step that moves more interrupt, recovery, and terminal boundary posture into the compiled graph state itself while preserving the seven-phase shell and the current durable artifacts.

## What Changes

- deepen the current live primary-engine beyond graph-carried next-hop state into graph-resident boundary state
- preserve the seven-phase operator shell, durable artifacts, and current inspectable control surfaces during the rollout
- keep the result additive to the current Codex leader model and existing LangGraph runtime layers

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-graph-resident-live-primary-engine-boundary-state`: graph-resident live primary-engine boundary-state semantics for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: deepen the live primary-engine beyond the current stateful transition posture into graph-resident boundary-state handling
- `codex-user-level-inspectable-team-state-surface`: expose graph-resident live-engine boundary-state posture without breaking the canonical durable-state summary
- `codex-user-level-team-mode-team-entrypoints`: expose additive inspection helpers for the graph-resident boundary-state lane

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
  - this change does not claim a fully generalized LangGraph-native runtime in one pass
  - this change does not reopen automatic-policy or subgraph-expansion work in the same mainline
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for graph-resident live-engine boundary-state posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
