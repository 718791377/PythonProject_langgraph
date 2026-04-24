## Why

The user-level LangGraph durable lane already persists repo-local thread state, checkpoints, reusable subgraph posture, replay or recovery controls, reducer-aware merge state, and command-driven handoff metadata. What it still lacks is an operator-facing streaming and debug observability surface aligned with the official LangGraph streaming model.

This gap matters now because current inspection remains snapshot-oriented. Without additive streaming for updates, checkpoints, tasks, debug events, and nested subgraph visibility, the operator still cannot watch graph-shaped work unfold with enough fidelity to diagnose stalls, noisy handoffs, or checkpoint churn in real time.

## What Changes

- Add a first-class user-level LangGraph streaming and debug observability surface.
- Define additive streaming contracts for operator-relevant event modes: `updates`, `checkpoints`, `tasks`, and `debug`.
- Define bounded support for multi-mode streaming and nested subgraph visibility under `subgraphs=True`.
- Persist stream-session posture and latest event summary in repo-local LangGraph durable state where needed for inspection.
- Expose streaming and debug helper surfaces through the existing user-level tooling and canonical durable-state projection.

## Capabilities

### New Capabilities
- `codex-user-level-langgraph-streaming-and-debug-observability-surface`: operator-facing LangGraph streaming and debug observability for the user-level durable lane

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: add streaming-mode, debug-event, checkpoint-event, and nested subgraph observability contracts
- `codex-user-level-inspectable-team-state-surface`: project latest streaming posture and relevant stream-helper pointers for tracked LangGraph threads
- `codex-user-level-team-mode-team-entrypoints`: expose additive LangGraph stream-observability entrypoints and playbook guidance

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` stream-session or latest-event metadata
  - LangGraph durable-state inspection and helper-pointer projections
  - LangGraph durable-team tests and install-surface integration tests
- explicit_non_goals:
  - this change does not change backend-selection policy
  - this change does not replace `native_omx` as the stable worker-centric default durable backend
  - this change does not introduce cloud-only tracing, LangSmith-hosted dashboards, or external observability infrastructure
  - this change does not redesign replay, recovery, reducer, loop, or command-driven semantics beyond stream-aware projection points
  - this change does not attempt a full chat-token UI or front-end rendering stack
- rollout_sequence:
  1. define proposal, design, and spec deltas for LangGraph streaming and debug observability
  2. extend the Python-side LangGraph contract layer with stream-mode and latest-event metadata
  3. add additive CLI and user-level helper surfaces for stream inspection
  4. project streaming posture and helper pointers through canonical durable-state inspection
  5. validate nested subgraph visibility, checkpoint and task observability, and debug-event projection
- rollback_plan:
  - revert only the streaming and observability contracts, projections, and helper-surface updates introduced by this change
  - keep the existing root graph, reusable subgraph library, command-driven control flow, replay or recovery controls, and reducer semantics intact
  - if stream output proves too noisy, keep backend-local latest-event tracking while disabling the user-level streaming helper surface
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for streaming-mode metadata and nested subgraph projection
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- mainline_classification:
  - existing Codex persistent agent-team mainline continuation
