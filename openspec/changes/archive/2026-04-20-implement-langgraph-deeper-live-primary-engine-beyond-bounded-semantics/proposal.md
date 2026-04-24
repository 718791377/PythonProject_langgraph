## Why

The repository has now closed the fuller live primary-execution-engine and richer automatic runtime-policy mainlines. After the latest capability-gap sync pass, the most concrete remaining runtime gap is deeper live-engine behavior beyond the current bounded primary execution semantics and helper-projected execution path.

The current engine can expose richer path and resulting-phase posture, but it still remains intentionally bounded. The next justified mainline is therefore a deeper live primary-engine step that expands execution semantics beyond the current bounded posture while preserving the seven-phase shell and existing durable artifacts.

## What Changes

- deepen the current live primary-execution engine beyond the present bounded execution semantics
- preserve the seven-phase operator shell, durable artifacts, and current inspectable control surfaces during the rollout
- keep the result additive to the current Codex leader model and existing LangGraph runtime layers

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-deeper-live-primary-engine-beyond-bounded-semantics`: deeper live primary-engine semantics for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: deepen the live primary-engine beyond current bounded semantics
- `codex-user-level-inspectable-team-state-surface`: expose deeper live-engine posture without breaking the canonical durable-state summary
- `codex-user-level-team-mode-team-entrypoints`: expose additive inspection helpers for the deeper live-engine lane

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
  - this change does not add cloud-only orchestration infrastructure
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for deeper live-engine posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
