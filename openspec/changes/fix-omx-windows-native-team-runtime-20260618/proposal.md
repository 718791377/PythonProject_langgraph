---
change_id: fix-omx-windows-native-team-runtime-20260618
status: proposed
owner: codex
created_at: 2026-06-18
---

# Proposal: Fix OMX Windows Native Team Runtime

## Why

User-level automatic collaboration currently treats `native_omx` as an eligible durable-team lane for worker-centric execution. On this machine, the failing condition is concrete: no local `tmux` is available and the active shell is not inside a `tmux` session, so a Unix/tmux-only pane implementation cannot launch a real persistent team.

The correction must not redefine `native_omx` as `tmux`. `native_omx` is the worker-centric durable backend family. `tmux` is only one Unix implementation backend inside that family. Native Windows needs its own runtime backend and its own operational-readiness evidence.

## What Changes

- Freeze the four-layer model: capability switches, backend family selection, task-flow effective lane, and operational ability.
- Freeze the rule that readiness or selection never implies launchability without runtime preflight evidence.
- Require Windows `native_omx` to use a native prompt/process controller backend by default when no Unix/tmux backend is explicitly requested.
- Require user-level helper output to expose `runtime_backend`, `preflight_passed`, `operational_ready`, and stable blocker tokens.
- Require `omx-team-auto.ps1 -Apply` to fail closed and avoid team-state mutation when operational preflight fails.
- Keep user-level assets under the user Codex home while every consumer repository owns its own `.omx/state/...` durable truth.

## Out of Scope

- Requiring WSL2 or installing Unix `tmux` as the native Windows default.
- Treating wrapper generation, planning output, or a tracked selector as proof that a real team launched.
- Moving consumer-project durable state into this repository.
- Remote publication, GitLab MR creation or merge, GitHub sync, or remote ref mutation.
