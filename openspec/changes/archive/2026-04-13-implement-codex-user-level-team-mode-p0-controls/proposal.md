## Why

The user-level team-mode plan is already stabilized, but the repository still lacks a safe implementation surface that can turn that plan into reusable assets for any Codex CLI project on the same Windows user profile.

The immediate need is a P0 control layer that is additive, testable, and reversible: it must generate user-level state and helper assets without replacing or breaking the native `codex` entrypoint.

## What Changes

- Add a repo-local installer/generator that can materialize Codex user-level team-mode control assets into an explicit target Codex home.
- Generate additive user-level assets for:
  - `team-leader.toml`
  - `codex-omx-on.ps1`
  - `codex-omx-off.ps1`
  - `codex-omx-status.ps1`
  - `codex-subagents-auto.ps1`
  - `codex-subagents-manual.ps1`
  - `codex-subagents-off.ps1`
  - `codex-routing-status.ps1`
- Introduce a single global state file that tracks `oh_my_codex` and `subagent_routing` as separate controls.
- Add install-time backup snapshots so failed writes can be rolled back automatically.
- Keep the generated assets additive and explicitly forbid creation or replacement of `codex`, `codex.cmd`, or `codex.ps1`.
- Add repository tests that validate generation, state switching, pure-debugging-mode semantics, and the "do not break native Codex" safety boundary.

## Capabilities

### New Capabilities

- `codex-user-level-team-mode-controls`
  - provide a reusable installer-generated control layer for user-level Codex and oh-my-codex team-mode state

### Modified Capabilities

- None.

## Impact

- Affected paths:
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `openspec/changes/implement-codex-user-level-team-mode-p0-controls/`
- This change does not modify OpenClaw runtime configuration.
- This change does not patch oh-my-codex internals.
- This change must not replace, shadow, or damage the native `codex` executable path.

## impact_scope

- repository-local installer and validation surface only
- user-level Codex home asset generation into an explicit target path
- additive control assets for `oh_my_codex` and `subagent_routing`
- versioned backup snapshots plus rollback-on-error behavior for generated assets
- safety boundary that preserves plain native Codex usability

## explicit_non_goals

- no direct in-repo mutation of `C:\Users\lenovo\.codex` during development or tests
- no replacement of the native `codex` entrypoint, shim, alias, or executable
- no implementation of mixed persistent pane compose mode in this P0 slice
- no implementation of persistent expert-pane orchestration in this P0 slice
- no repository-specific OpenClaw runtime or proxy behavior change
- no WSL2-based path

## rollout_sequence

1. Create the OpenSpec artifacts for the P0 control surface.
2. Implement a repo-local installer/generator that targets an explicit Codex home path.
3. Generate additive control assets plus the leader profile and shared state file.
4. Add backup snapshot creation before writes and automatic rollback after partial failure.
5. Validate state transitions for `on/off/auto/manual`, pure debugging mode, and rollback behavior.
6. Verify that native `codex`-named files are not created, replaced, or modified by the generator.
7. Leave richer wrappers such as hybrid staffing or compose manifests for later phases.

## rollback_plan

- Remove the installer and its tests if the generated surface proves misleading or unsafe.
- Remove the new capability artifacts if the repository chooses a different user-level control model.
- Keep the rollback narrow: revert only the repo-local generator and change artifacts rather than touching any user home assets created outside the repository.

## validation_path

- run the dedicated PowerShell test for generation and state transitions
- verify the generated assets stay inside an explicit target Codex home path
- verify unmanaged collisions are rejected by default
- verify a failed install restores the pre-install managed state from a backup snapshot
- verify `codex`, `codex.cmd`, and `codex.ps1` are never created or overwritten by the installer
- run `openspec validate --all`
- run `python .\tools\run_openspec_guard.py --root .`

## mainline_classification

- new mainline candidate
- cross-project Codex and oh-my-codex user-level workflow infrastructure
- cross-mainline in effect because it spans reusable tooling, validation, and governance, but it is not owned by an existing OpenClaw runtime mainline
