## Why

The repository has now closed the reducer-aware live primary-engine merge-state mainline and the follow-up capability-gap sync pass. The most concrete remaining live-engine gap is no longer reducer-aware merge posture; it is command-aware control state inside the live primary engine itself.

The current LangGraph lane already exposes command-driven control flow, explicit `goto` handling, explicit parent handoffs, resume posture, and bounded command projection surfaces. But transition kind, update keys, goto target, graph scope, source and target subgraph attribution, parent-handoff target, and resume-payload posture still primarily live in an adjacent command projection rather than in the live-engine state itself.

The next justified mainline is therefore a command-aware live primary-engine control-state step that moves more command and handoff control semantics into live-engine state while preserving the seven-phase shell, durable artifacts, reducer posture, and current inspectable control surfaces.

## What Changes

- deepen the current live primary-engine beyond reducer-aware merge-state into command-aware control-state handling
- preserve the seven-phase operator shell, durable artifacts, reducer posture, and current inspectable control surfaces during the rollout
- keep the result additive to the current Codex leader model and existing LangGraph runtime layers

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-command-aware-live-primary-engine-control-state`: command-aware live primary-engine control-state semantics for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: deepen the live primary-engine beyond the current reducer-aware posture into command-aware control handling
- `codex-user-level-inspectable-team-state-surface`: expose command-aware live-engine posture without breaking the canonical durable-state summary
- `codex-user-level-team-mode-team-entrypoints`: expose additive user-level command-aware live-engine entrypoints

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
  - targeted Python tests for command-aware live-engine posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
