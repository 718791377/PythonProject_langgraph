## Why

The archived `P6` batch established a native Windows durable-team backend, but follow-up live validation exposed two Windows-specific gaps that should be tracked as a separate correction batch instead of being silently folded back into the archived change:

- worker controller processes launched as ordinary detached children could still die with the parent shell on native Windows
- Windows prompt-worker guidance still encouraged duplicate startup ACK / claim attempts and brittle `--input` JSON patterns under constrained PowerShell

The platform therefore needs a focused follow-up batch that formalizes breakaway worker launch, pid-accurate lifecycle tracking, and Windows-safe controller-owned startup behavior.

## What Changes

- harden the native Windows prompt-worker launch path so durable workers survive parent shell exit
- make worker pid tracking reflect the real long-lived controller process rather than a short-lived launcher hop
- keep `status / await / shutdown` semantics aligned with the new launcher shape
- reduce Windows startup noise by teaching worker guidance that controller-managed ACK and initial claim may already be complete
- keep repo-local team state isolation and runtime-root isolation unchanged

- impact_scope:
  - native Windows durable-team runtime
  - worker lifecycle tracking
  - worker bootstrap guidance

- explicit_non_goals:
  - no WSL2 path
  - no Unix `tmux` changes
  - no change to native Codex preservation policy
  - no new mixed persistent pane compose layer

- rollout_sequence:
  1. formalize the correction batch and acceptance surface
  2. implement a Windows breakaway launcher path for prompt workers
  3. align shutdown and liveness tracking with the launched controller pid
  4. update Windows worker guidance for controller-owned ACK / claim behavior
  5. rerun native Windows live validation

## Capabilities

### Modified Capabilities
- `codex-user-level-team-mode-windows-native-team-backend`

## Impact

- affected_code:
  - oh-my-codex team runtime
  - Windows worker controller launch path
  - worker bootstrap guidance
- systems:
  - native Windows durable team lifecycle
  - repo-local team state and tracked-team operation
