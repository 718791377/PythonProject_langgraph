## Why

The user-level LangGraph durable lane already has additive backend selection, repo-local durable state, reusable subgraph contracts, bounded quality-gated loops, replay or recovery controls, and reducer-aware merge semantics. What it still lacks is LangGraph's explicit command-driven control-flow layer, especially `Command(update/goto/graph/resume)` and parent-targeted handoffs between subgraphs.

This gap matters now because the current local lane still behaves more like a structured durable wrapper than a strongly graph-native runtime. Without explicit command-driven transitions and inspectable parent handoffs, multi-agent routing across reusable subgraphs remains less expressive, less auditable, and less aligned with the official LangGraph control-flow model.

## What Changes

- Add a first-class user-level command-driven control-flow contract for the LangGraph durable lane.
- Define additive support for explicit `Command`-style state update plus route selection, including `goto`, `resume`, and parent-directed handoff posture.
- Define how reusable subgraph boundaries declare parent-handoff exits instead of relying only on phase-family inference.
- Persist command-driven transition metadata and parent-handoff attribution in repo-local LangGraph durable state.
- Expose command-driven transition posture through the canonical inspectable durable-state surface without changing backend-selection policy.

## Capabilities

### New Capabilities
- `codex-user-level-langgraph-command-driven-control-flow`: command-driven transition and parent-handoff contracts for the user-level LangGraph durable lane

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: add explicit command-driven routing, parent-directed handoff, and resume-payload semantics for tracked LangGraph threads
- `codex-user-level-inspectable-team-state-surface`: project command-driven transition posture and parent-handoff metadata for tracked LangGraph threads
- `codex-user-level-langgraph-reusable-subgraph-library`: declare command-aware subgraph exit and handoff boundaries instead of treating subgraphs as passive role bundles only

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` thread and checkpoint metadata
  - LangGraph durable-state inspection and helper-pointer projections
  - LangGraph durable-team tests and install-surface integration tests
- explicit_non_goals:
  - this change does not change backend-selection policy
  - this change does not replace `native_omx` as the stable worker-centric default durable backend
  - this change does not redesign replay, recovery, reducer, or quality-gated loop semantics beyond command-aware integration points
  - this change does not introduce cloud-only LangGraph deployment infrastructure
  - this change does not make every reusable subgraph directly user-launchable as an always-on worker lane
- rollout_sequence:
  1. define proposal, design, and spec deltas for command-driven control flow and parent handoffs
  2. extend the Python-side LangGraph contract layer with command and parent-handoff metadata
  3. persist command-driven transition posture in tracked thread and checkpoint state
  4. expose command-aware inspection through existing LangGraph tooling and canonical durable-state projection
  5. validate durable-state attribution, parent-handoff posture, and bounded resume semantics
- rollback_plan:
  - revert only the command-driven control-flow contracts, projections, and helper-surface updates introduced by this change
  - keep the existing root graph, reusable subgraph library, loops, replay or recovery controls, and reducer semantics intact
  - if parent-handoff posture proves too noisy, keep command-aware state local to the backend while disabling the new inspection projection fields
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for command-driven transition metadata and parent-handoff projection
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- mainline_classification:
  - existing Codex persistent agent-team mainline continuation
