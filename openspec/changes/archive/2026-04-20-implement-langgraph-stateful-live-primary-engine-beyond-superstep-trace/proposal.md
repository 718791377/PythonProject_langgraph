## Why

The repository has now closed the superstep live primary-engine mainline and the follow-up capability-gap sync pass. The most concrete remaining runtime gap is no longer multi-node trace projection; it is the statefulness of the live primary engine itself.

The current `superstep-engine` lane can traverse a bounded multi-node compiled graph path and project node or phase visit traces, superstep counts, and bounded stop-boundary posture. But routing and continuation decisions are still computed outside the compiled graph first and then handed into the graph as a prepared trace.

The next justified mainline is therefore a stateful live primary-engine step that moves more live routing and continuation semantics into the graph-native execution state itself while preserving the seven-phase shell and the current durable artifacts.

## What Changes

- deepen the current live primary-engine beyond precomputed superstep trace posture
- preserve the seven-phase operator shell, durable artifacts, and current inspectable control surfaces during the rollout
- keep the result additive to the current Codex leader model and existing LangGraph runtime layers

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-stateful-live-primary-engine-beyond-superstep-trace`: stateful live primary-engine semantics for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: deepen the live primary-engine beyond the current superstep trace posture
- `codex-user-level-inspectable-team-state-surface`: expose stateful live-engine posture without breaking the canonical durable-state summary
- `codex-user-level-team-mode-team-entrypoints`: expose additive inspection helpers for the stateful live-engine lane

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
  - targeted Python tests for stateful live-engine posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
