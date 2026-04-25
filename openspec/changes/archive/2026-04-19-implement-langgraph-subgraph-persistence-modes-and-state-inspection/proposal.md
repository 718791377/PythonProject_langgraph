## Why

The generalized live `StateGraph` routing mainline is now closed, which means the next LangGraph-deepening gap is no longer the top-level route shell. The next concrete gap is inside reusable subgraphs: the repository has reusable subgraph contracts and active-subgraph posture, but it still does not formalize or expose the official subgraph persistence modes and subgraph-state inspection semantics from the LangGraph subgraphs guide.

The official LangGraph model distinguishes three subgraph persistence modes through the `checkpointer` argument on `.compile()`:

- per-invocation: `None` (default)
- per-thread: `True`
- stateless: `False`

It also documents important inspection boundaries such as `get_state(config, subgraphs=True)` only being available when checkpoints exist and the subgraph can be statically discovered.

## What Changes

- Introduce explicit subgraph persistence-mode posture for the user-level LangGraph lane.
- Project per-invocation, per-thread, and stateless subgraph behavior into durable thread state and operator inspection surfaces.
- Expose bounded subgraph-state inspection posture and availability constraints for tracked LangGraph threads.
- Keep the rollout additive to the existing reusable subgraph library and generalized live-routing layers.

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-subgraph-persistence-modes-and-state-inspection`: additive user-level subgraph persistence and inspection capability

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: add official subgraph persistence-mode and state-inspection posture
- `codex-user-level-inspectable-team-state-surface`: expose subgraph persistence-mode and state-inspection projection for tracked LangGraph threads
- `codex-user-level-team-mode-team-entrypoints`: expose an additive user-level subgraph-state inspection helper

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` subgraph posture records and projections
  - LangGraph Python tests and install-surface integration tests
- explicit_non_goals:
  - this change does not replace the current reusable subgraph library contract
  - this change does not replace generalized live routing
  - this change does not claim full parity with every subgraph feature beyond persistence modes and inspectability
  - this change does not redesign the leader model away from the current Codex CLI session
- rollout_sequence:
  1. define delta specs for subgraph persistence modes and state inspection
  2. extend the Python LangGraph contract and projection layer with official persistence-mode posture
  3. expose additive subgraph-state inspection surfaces for user-level tooling and durable-state status
  4. validate the new posture without regressing current reusable subgraph or live-routing surfaces
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for subgraph persistence-mode and state-inspection posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- sources:
  - `https://docs.langchain.com/oss/python/langgraph/use-subgraphs`
