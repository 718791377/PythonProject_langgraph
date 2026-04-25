## Why

The current Codex / oh-my-codex durable workflow already supports leader-side native subagents, homogeneous durable worker teams, startup routing, and repo-local runtime isolation, but it still lacks a true persistent orchestration kernel for long-running multi-step execution across checkpoints, interrupts, and resumable graph state. LangGraph is now a strong fit for that missing layer because it is explicitly designed for long-running, stateful workflows with persistence, interrupts, subgraphs, and durable execution.

## What Changes

- Add a LangGraph-based durable orchestration backend that runs under the existing `Codex CLI + oh-my-codex` workflow instead of replacing it.
- Keep `Codex CLI` as the leader and final integrator, keep expert roles bursty, and use LangGraph as the persistent orchestration kernel for long-running execution flows.
- Define a seven-phase root graph that matches the existing development flow and uses subgraphs for research, planning, execution, verification, and stabilization.
- Persist research-to-implementation handoff as a frozen implementation brief and require implementation to continue in a fresh execution context instead of reusing open-ended research context.
- Persist adversarial bug review as a queue of judge-approved survivors consumed by a durable debugger lane rather than turning `bug-finder / bug-rebutter / bug-judge` into default persistent workers.
- Add repo-local `.omx` bridge rules for LangGraph threads, checkpoints, interrupts, store data, and backend metadata.
- Add user-level controls and entrypoints so operators can select the durable orchestration backend and inspect LangGraph thread status and resumability.

## Capabilities

### New Capabilities
- `langgraph-durable-orchestration-backend`: LangGraph-backed durable orchestration integrated with the existing Codex / oh-my-codex leader model, including graph persistence, interrupts, subgraphs, research handoff, adversarial-review survivor queues, and `.omx` bridge rules

### Modified Capabilities
- `codex-user-level-team-mode-controls`: add explicit durable orchestration backend selection and LangGraph runtime-state surfaces to the generated user-level controls
- `codex-user-level-team-mode-team-entrypoints`: add LangGraph-oriented run/status/resume/inspect entrypoints and playbook guidance
- `codex-user-level-team-mode-automatic-team-routing`: allow automatic durable routing to choose the LangGraph backend when that backend is selected

## Impact

- impact_scope:
  - user-level Codex / oh-my-codex control assets
  - persistent orchestration runtime and state layout under `.omx`
  - generated playbook and operator entrypoints
  - OpenSpec specs for controls, entrypoints, and automatic durable routing
- explicit_non_goals:
  - no replacement of native `codex`, `codex.cmd`, or `codex.ps1`
  - no removal of the current `omx team` backend
  - no default mixed persistent pane topology
  - no WSL2 requirement
  - no conversion of expert roles into always-on persistent workers
- rollout_sequence:
  - define proposal, design, and spec contracts for LangGraph integration
  - add backend-selection controls and LangGraph state layout
  - add LangGraph run/status/resume/inspect entrypoints
  - add LangGraph MVP backend and graph skeleton
  - validate interrupt/resume, thread persistence, handoff persistence, and survivor-queue flow
- rollback_plan:
  - keep LangGraph integration additive and backend-selectable
  - preserve the current direct `omx team` path as the rollback-safe fallback
  - if LangGraph orchestration fails or remains incomplete, switch the backend selector back to the current native durable path
- validation_path:
  - run `openspec validate --all`
  - validate generated control assets and backend-selection status output
  - validate one persisted LangGraph thread across restart or resume
  - validate interrupt -> human approval -> resume
  - validate research brief persistence and fresh execution-context restart
  - validate adversarial bug-review survivor queue feeding a debugger lane
- mainline_classification:
  - existing mainline continuation
  - specifically a durable-orchestration backend expansion under the Codex / oh-my-codex team-mode line
