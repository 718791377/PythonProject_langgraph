## Why

The repository has now closed the graph-resident live primary-engine boundary-state mainline and the follow-up capability-gap sync pass. The most concrete remaining runtime gap is no longer graph-resident boundary handling alone; it is subgraph-aware handoff state inside the live primary engine itself.

The current live-engine line now carries next-hop decisions, transition logs, and boundary posture in graph-native state. But subgraph identity, parent handoff targets, and handoff-specific continuation posture are still primarily projected from adjacent command and subgraph surfaces rather than being carried as first-class live-engine state.

The next justified mainline is therefore a subgraph-aware live primary-engine handoff-state step that moves more subgraph and parent-handoff semantics into the live-engine state itself while preserving the seven-phase shell and the current durable artifacts.

## What Changes

- deepen the current live primary-engine beyond graph-resident boundary handling into subgraph-aware handoff state
- preserve the seven-phase operator shell, durable artifacts, and current inspectable control surfaces during the rollout
- keep the result additive to the current Codex leader model and existing LangGraph runtime layers

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-subgraph-aware-live-primary-engine-handoff-state`: subgraph-aware live primary-engine handoff-state semantics for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: deepen the live primary-engine beyond the current graph-resident boundary-state posture into subgraph-aware handoff handling
- `codex-user-level-inspectable-team-state-surface`: expose subgraph-aware live-engine handoff posture without breaking the canonical durable-state summary
- `codex-user-level-team-mode-team-entrypoints`: expose additive inspection helpers for the subgraph-aware handoff-state lane

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
  - targeted Python tests for subgraph-aware live-engine handoff posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
