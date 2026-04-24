## Why

The repository has now closed the command-aware live primary-engine control-state mainline and the follow-up capability-gap sync pass. The most concrete remaining live-engine gap is no longer command-aware control posture; it is runtime-aware context and store state inside the live primary engine itself.

The current LangGraph lane already exposes `context_schema`, runtime-context presence and keys, store configuration posture, store access expectations, and store kind through the adjacent runtime injection projection. But those runtime-context and store semantics still primarily live in that adjacent projection rather than in the live-engine state itself.

The next justified mainline is therefore a runtime-aware live primary-engine context-store step that moves more runtime-context and injected-store semantics into live-engine state while preserving the seven-phase shell, durable artifacts, command-aware control posture, and current inspectable control surfaces.

## What Changes

- deepen the current live primary-engine beyond command-aware control-state into runtime-aware context-store handling
- preserve the seven-phase operator shell, durable artifacts, command posture, and current inspectable control surfaces during the rollout
- keep the result additive to the current Codex leader model and existing LangGraph runtime layers

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-runtime-aware-live-primary-engine-context-store-state`: runtime-aware live primary-engine context-store semantics for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: deepen the live primary-engine beyond the current command-aware posture into runtime-context and injected-store handling
- `codex-user-level-inspectable-team-state-surface`: expose runtime-aware live-engine posture without breaking the canonical durable-state summary
- `codex-user-level-team-mode-team-entrypoints`: expose additive user-level runtime-aware live-engine entrypoints

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
  - targeted Python tests for runtime-aware live-engine posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
