---
change_id: fix-omx-windows-native-team-runtime-20260618
status: proposed
owner: codex
created_at: 2026-06-18
---

# Design: OMX Windows Native Team Runtime

## Four-Layer Model

Stage A freezes four distinct layers:

1. Capability switches: `subagent_routing`, `oh_my_codex`, and `langgraph` say which layers are enabled.
2. Backend family: `native_omx` and `langgraph` name durable backend families.
3. Effective lane: the current task flow selects the lane that fits the work, such as worker-centric native OMX or graph-shaped LangGraph.
4. Operational ability: the selected lane can actually launch, reuse, inspect, await, resume, and shut down now.

These layers must not be used as synonyms. In particular, `selected=true` and `ready=true` do not prove operational ability.

## Runtime Backend Contract

Inside the `native_omx` family, `runtime_backend` names the concrete implementation backend. Required values are stable strings, with room for future extensions:

- `windows_prompt_process_controller` for the native Windows default.
- `unix_tmux` for the Unix/tmux backend.
- `unknown` when no runtime backend can be proven.

On Windows, when the operator has not explicitly requested a Unix/tmux backend, the automatic team helper must select or preflight `windows_prompt_process_controller`. It must not fail only because `tmux` is missing, and it must not silently downgrade to a false launch record.

## Preflight And Blockers

Operational preflight must report:

- `runtime_backend` - concrete runtime implementation backend.
- `preflight_passed` - whether operational preflight passed.
- `operational_ready` - whether launch/reuse/status lifecycle operations are currently possible.
- `blockers` - stable named blocker tokens.

Stable blocker tokens include:

- `blocked:windows_backend_not_implemented` - Windows controller backend is not implemented yet.
- `blocked:backend_not_ready` - selected durable backend is not ready for the requested operation.
- `blocked:tmux_only_backend` - only a Unix/tmux runtime backend is available.
- `blocked:not_in_tmux_session` - a tmux-specific operation is running outside a tmux session.
- `blocked:controller_launch_failed` - the Windows controller launch attempt failed.
- `blocked:breakaway_process_unavailable` - the required Windows breakaway process path is unavailable.
- `blocked:runtime_backend_unavailable` - no concrete runtime backend can be used now.
- `blocked:selector_refresh_gap` - selector state must be refreshed before launch.

When preflight fails, `omx-team-auto.ps1 -Apply` must return a structured blocked result and avoid mutating tracked team state, active selectors, or fake launch receipts.

## Cross-Project Boundary

The installed user-level assets live under the user Codex home, such as `C:\Users\lenovo\.codex`. Every repository keeps its own `.omx/state/...` records. A consumer repository must be able to use the installed OMX runtime from its own current working directory without depending on `D:\PythonProject_langgraph` as the runtime cwd.

## Stage B Slices

After this Stage A package is integrated into local `main`, Stage B has at least two mostly independent slices:

1. Readiness, backend-selection, and `omx-team-auto.ps1 -Apply` fail-closed behavior.
2. Native Windows prompt/process controller launch and lifecycle evidence.
3. Cross-project install/smoke validation and documentation alignment.

The leader owns final fan-in, validation, local commit, local `main` integration, cleanup, and the remote-publication stop.
