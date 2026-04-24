## Why

Current user-level team mode already installs:

- wrapped startup
- routing thresholds
- `team-leader.toml`
- durable-team helpers

What is still missing is a strong startup-time binding that makes every new wrapped Codex session reliably behave like a leader-first routed session.

Today, new sessions receive dynamic `developer_instructions`, but they do not always:

- classify the task shape before the first substantive answer
- explain whether expert native subagents should be called
- explain whether `omx team` thresholds were met
- emit an inspectable routing trace

The next batch should therefore formalize startup leadership binding and first-turn routing behavior.

## What Changes

- strengthen wrapped startup so every new wrapped Codex session enters a stable leader-first routing posture
- bind startup behavior more explicitly to the installed `team-leader` role model instead of treating it as an unused side asset
- make startup produce a short first-turn routing trace
- require startup to explain why `omx team` was selected or not selected
- keep startup classification separate from automatic durable-team launch

- impact_scope:
  - wrapped `codex` startup path
  - user-level leader protocol binding
  - first-turn routing observability

- explicit_non_goals:
  - no automatic durable-team launch on every new session
  - no change to the native Codex bypass path
  - no change to the global control meanings of `oh_my_codex` and `subagent_routing`

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-startup-leader-protocol`

### Modified Capabilities
- `codex-user-level-team-mode-startup-binding`
- `codex-user-level-team-mode-routing-thresholds`

## Impact

- affected_code:
  - user-level startup launcher
  - startup-bound developer instruction assembly
  - user-visible routing trace surface
- systems:
  - wrapped Codex session startup
  - leader-side routing explainability
