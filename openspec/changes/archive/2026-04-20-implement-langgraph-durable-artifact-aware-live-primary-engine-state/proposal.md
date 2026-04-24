## Why

The repository has now closed the recovery-aware live primary-engine provenance-state mainline and the follow-up capability-gap sync pass. The most concrete remaining runtime gap is no longer recovery-aware provenance posture; it is durable-artifact-aware state inside the live primary engine itself.

The current live-engine line now carries next-hop decisions, graph-resident boundary posture, subgraph-aware handoff semantics, approval-aware resume state, and recovery-aware provenance state in graph-native state. But durable artifacts such as the frozen implementation brief and judge-approved survivor queue are still primarily projected from adjacent artifact surfaces rather than being carried as first-class live-engine state.

The next justified mainline is therefore a durable-artifact-aware live primary-engine step that moves more implementation-brief and survivor-queue semantics into the live-engine state itself while preserving the seven-phase shell and the current durable artifacts.

## What Changes

- deepen the current live primary-engine beyond recovery-aware provenance state into durable-artifact-aware state
- preserve the seven-phase operator shell, durable artifacts, and current inspectable control surfaces during the rollout
- keep the result additive to the current Codex leader model and existing LangGraph runtime layers

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-durable-artifact-aware-live-primary-engine-state`: durable-artifact-aware live primary-engine semantics for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: deepen the live primary-engine beyond the current recovery-aware provenance-state posture into durable-artifact-aware handling
- `codex-user-level-inspectable-team-state-surface`: expose durable-artifact-aware live-engine posture without breaking the canonical durable-state summary
- `codex-user-level-team-mode-team-entrypoints`: expose additive inspection helpers for the durable-artifact-aware lane

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
  - targeted Python tests for durable-artifact-aware live-engine posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
