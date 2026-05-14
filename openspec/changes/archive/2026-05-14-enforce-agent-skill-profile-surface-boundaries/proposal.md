# Change: Enforce agent, skill, and profile surface boundaries

## Why

The automatic orchestration routing plan requires native Codex agents, workflow skills, plugin-provided skills, profile helpers, and expert evidence to remain distinct execution surfaces. Existing checks validate custom agent TOML minimum fields, but they do not fail when policy surfaces or trace evidence collapse skills/profiles into native subagents or treat skill/profile invocation as expert evidence.

## What Changes

- Add a repository/evidence checker for native agent, skill, plugin profile, and expert evidence boundaries.
- Wire the checker into the shared OpenSpec guard and local/remote CI manifest.
- Register the checker as script backing for the orchestration activation policy.
- Extend the stable orchestration activation spec with explicit surface-boundary requirements.

## Capabilities

- codex-user-level-orchestration-activation-policy

## Impact

- Affects orchestration governance checks and local/remote CI only.
- Does not change runtime routing behavior directly.
- Keeps custom agent TOML schema validation as a separate but related checker.
