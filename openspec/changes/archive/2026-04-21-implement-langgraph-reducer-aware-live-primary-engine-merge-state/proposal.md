## Why

The repository has now closed the durable-artifact-aware live primary-engine state mainline and the follow-up capability-gap sync pass. The most concrete remaining live-engine gap is no longer artifact-aware posture; it is reducer-aware merge posture inside the live primary engine itself.

The current LangGraph lane already exposes reducer-backed merge channels, single-writer protection, fan-in or fan-out projection fields, durable artifacts, and the deeper live-engine ladder through durable-artifact-aware state. But reducer compatibility, fanout state, multi-writer violation posture, merge-channel updates, and reducer source attribution still primarily live in an adjacent reducer projection rather than in the live-engine state itself.

The next justified mainline is therefore a reducer-aware live primary-engine merge-state step that moves more reducer and merge semantics into live-engine state while preserving the seven-phase shell, durable artifacts, and current inspectable control surfaces.

## What Changes

- deepen the current live primary-engine beyond durable-artifact-aware state into reducer-aware merge-state handling
- preserve the seven-phase operator shell, durable artifacts, and current inspectable control surfaces during the rollout
- keep the result additive to the current Codex leader model and existing LangGraph runtime layers

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-reducer-aware-live-primary-engine-merge-state`: reducer-aware live primary-engine merge-state semantics for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: deepen the live primary-engine beyond the current durable-artifact-aware posture into reducer-aware merge handling
- `codex-user-level-inspectable-team-state-surface`: expose reducer-aware live-engine posture without breaking the canonical durable-state summary
- `codex-user-level-team-mode-team-entrypoints`: expose additive user-level reducer-aware live-engine entrypoints

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
  - targeted Python tests for reducer-aware live-engine posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
