## Why

P5 completed the automatic durable-team routing layer, but real `omx team -Apply` execution on native Windows is still blocked because the runtime currently requires `tmux`. The next batch is therefore not another routing change, but a Windows-native durable-team backend that lets the existing user-level team-mode surface actually run without WSL2.

## What Changes

- Add a native Windows durable-team backend for `omx team` so worker launch, status, await, resume, and shutdown can run without WSL2 or Unix `tmux`.
- Keep the existing Unix `tmux` path as a separate backend instead of trying to replace it.
- Preserve the repo-local `.omx/state/team/...` state, mailbox, heartbeat, and worktree contract across backends.
- Make generated wrappers such as `omx-team-dev.ps1`, `omx-team-debug.ps1`, and `omx-team-auto.ps1` backend-neutral so they work on Windows once a supported backend is present.
- Keep the native Codex base layer unchanged and preserve the current user-level backup and rollback model.
- impact_scope:
  - oh-my-codex team runtime
  - user-level team-mode wrappers and policy guidance
  - Windows-only durable worker lifecycle
- explicit_non_goals:
  - no WSL2 dependency
  - no replacement of native `codex.cmd` or native `omx.cmd`
  - no default mixed persistent pane compose layer
  - no forced GUI pane automation as the first implementation strategy
- rollout_sequence:
  1. define the Windows backend contract and acceptance surface
  2. add backend abstraction under `omx team`
  3. implement a native Windows durable-team backend
  4. validate launch, status, await, resume, shutdown, and `omx-team-auto.ps1 -Apply`
- rollback_plan:
  - keep the user-level wrapper surface reversible through the existing installer backup snapshots
  - keep the runtime backend change isolated so native Codex and non-team paths remain unaffected
- validation_path:
  - backend-specific runtime tests
  - user-level wrapper validation on native Windows
  - `openspec validate --all`
  - `python .\tools\run_openspec_guard.py --root .`
- mainline_classification:
  - existing mainline: Codex / oh-my-codex user-level team mode

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-windows-native-team-backend`: native Windows durable-team backend contract for `omx team`

### Modified Capabilities
- `codex-user-level-team-mode-team-entrypoints`: generated team entrypoint wrappers must stay usable on native Windows without assuming Unix `tmux`
- `codex-user-level-team-mode-automatic-team-routing`: `omx-team-auto.ps1 -Apply` must be able to execute its tracked durable-team decisions on native Windows once the backend is present

## Impact

- Affected code:
  - oh-my-codex runtime team backend implementation
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `openspec/changes/implement-codex-user-level-team-mode-p6-windows-native-team-backend/`
- Systems:
  - native Windows durable team runtime
  - repo-local `.omx` team state lifecycle
  - `omx-team-auto.ps1 -Apply` on native Windows
