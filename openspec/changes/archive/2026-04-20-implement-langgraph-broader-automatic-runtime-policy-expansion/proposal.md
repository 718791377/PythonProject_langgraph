## Why

The repository has now landed a bounded automatic runtime-policy layer that covers safe migration continuation and resolved-queue auto-resume. After the latest capability-gap sync pass, the most concrete remaining gap is broader automatic runtime-policy expansion beyond that initial bounded posture.

The current lane is still intentionally manual-first. That is correct, but the remaining future-work queue now points at a specific next direction: broader automatic-policy behavior that stays inspectable, bounded, and operator-visible rather than silent or unbounded.

## What Changes

- expand the current automatic runtime-policy layer beyond the initial bounded posture
- keep the rollout manual-first, inspectable, and bounded by explicit policy contracts
- preserve the current seven-phase shell, durable artifacts, and current user-level helper surfaces

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-broader-automatic-runtime-policy-expansion`: broader bounded automatic-policy behavior for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: broaden bounded automatic runtime-policy behavior beyond the initial migration and resolved-queue posture
- `codex-user-level-inspectable-team-state-surface`: expose richer automatic-policy posture for tracked LangGraph threads
- `codex-user-level-team-mode-team-entrypoints`: expose additive inspection helpers for the broader automatic-policy lane

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` runtime-policy projection data
  - LangGraph Python tests and install-surface integration tests
- explicit_non_goals:
  - this change does not replace manual-first operator control
  - this change does not silently auto-switch backend family
  - this change does not redesign the Codex CLI leader model
  - this change does not land unbounded autonomous policy behavior
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for broader automatic runtime-policy posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
