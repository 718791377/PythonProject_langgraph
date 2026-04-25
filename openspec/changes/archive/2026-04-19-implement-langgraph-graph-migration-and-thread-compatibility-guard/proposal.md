## Why

The user-level LangGraph durable lane now has additive backend selection, reusable subgraphs, replay or recovery controls, command-driven handoffs, streaming observability, runtime/store injection, and bounded memory-store posture. What it still lacks is an explicit graph-migration and thread-compatibility guard aligned with the official LangGraph graph migration model.

This gap matters now because the local lane keeps evolving its graph contracts while persisting repo-local threads. Without a compatibility guard, later topology or state-schema changes can silently strand older threads, overstate safety for resumed work, or blur the difference between migration-safe changes and changes that require explicit operator intervention.

## What Changes

- Add a first-class graph-migration and thread-compatibility guard for the user-level LangGraph durable lane.
- Define additive compatibility classification for tracked threads against current graph topology and state-schema posture.
- Define bounded operator-facing signals for migration-safe, degraded-compatible, and incompatible thread states.
- Persist migration posture and compatibility findings in repo-local LangGraph durable state.
- Expose migration and compatibility posture through the canonical inspectable durable-state surface and generated user-level helper surfaces.

## Capabilities

### New Capabilities
- `codex-user-level-langgraph-graph-migration-and-thread-compatibility-guard`: graph migration and thread-compatibility contracts for the user-level LangGraph durable lane

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: add graph-migration compatibility classification and thread-compatibility guard semantics for tracked LangGraph threads
- `codex-user-level-inspectable-team-state-surface`: project migration and compatibility posture for tracked LangGraph threads
- `codex-user-level-team-mode-team-entrypoints`: expose additive migration/compatibility inspection entrypoints and playbook guidance

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` compatibility metadata
  - LangGraph durable-state inspection and helper-pointer projections
  - LangGraph durable-team tests and install-surface integration tests
- explicit_non_goals:
  - this change does not change backend-selection policy
  - this change does not replace `native_omx` as the stable worker-centric default durable backend
  - this change does not attempt automatic graph rewrites or silent state repair for incompatible threads
  - this change does not redesign replay, recovery, reducer, command-driven, streaming, runtime/store, or memory semantics beyond compatibility-aware integration points
  - this change does not introduce cloud-only migration orchestration infrastructure
- rollout_sequence:
  1. define proposal, design, and spec deltas for graph migration and thread compatibility
  2. extend the Python-side LangGraph contract layer with compatibility classification and migration metadata
  3. persist bounded graph-migration and thread-compatibility posture through tracked thread and backend projection state
  4. expose migration/compatibility inspection through existing tooling and generated helper surfaces
  5. validate migration-safe versus incompatible thread classification without forcing automatic migration
- rollback_plan:
  - revert only the migration and compatibility contracts, projections, and helper-surface updates introduced by this change
  - keep the existing root graph, reusable subgraph library, command-driven control flow, streaming surfaces, runtime/store injection, memory posture, replay or recovery controls, and reducer semantics intact
  - if compatibility posture proves too noisy, keep backend-local classification while disabling the user-level projection fields
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for migration posture and thread-compatibility classification
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- mainline_classification:
  - existing Codex persistent agent-team mainline continuation
