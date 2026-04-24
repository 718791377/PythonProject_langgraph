## Why

The repository has now closed the runtime-aware live primary-engine context-store-state mainline and the follow-up capability-gap sync pass. The most concrete remaining live-engine gap is no longer runtime-aware context-store posture; it is memory-aware semantic state inside the live primary engine itself.

The current LangGraph lane already exposes memory-store configuration, memory namespaces, semantic-memory posture, semantic-store kind, and semantic namespaces through the adjacent memory projection. But those durable memory and semantic-memory semantics still primarily live in that adjacent projection rather than in the live-engine state itself.

The next justified mainline is therefore a memory-aware live primary-engine semantic-state step that moves more memory-store and semantic-memory semantics into live-engine state while preserving the seven-phase shell, durable artifacts, runtime-aware context-store posture, and current inspectable control surfaces.

## What Changes

- deepen the current live primary-engine beyond runtime-aware context-store-state into memory-aware semantic-state handling
- preserve the seven-phase operator shell, durable artifacts, runtime-aware posture, and current inspectable control surfaces during the rollout
- keep the result additive to the current Codex leader model and existing LangGraph runtime layers

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-memory-aware-live-primary-engine-semantic-state`: memory-aware live primary-engine semantic-state semantics for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: deepen the live primary-engine beyond the current runtime-aware posture into memory-store and semantic-memory handling
- `codex-user-level-inspectable-team-state-surface`: expose memory-aware live-engine posture without breaking the canonical durable-state summary
- `codex-user-level-team-mode-team-entrypoints`: expose additive user-level memory-aware live-engine entrypoints

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
  - targeted Python tests for memory-aware live-engine posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
