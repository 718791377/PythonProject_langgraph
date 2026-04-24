## Why

P0 and P1 made the user-level state model and startup binding real, but they still leave day-to-day `omx team` operation too manual. The next gap is a reusable operator surface that works across repositories, preserves the native Codex base layer, and encodes the approved homogeneous-team-plus-expert-burst workflow without forcing repository-specific scripts.

## What Changes

- Add user-level `omx team` entrypoint wrappers for development, debugging, operations, hybrid staffing, and verification planning.
- Extend the installer so it can generate and back up the new entrypoint assets in the target Codex home.
- Generate a user-level playbook that documents mode meanings, wrapper usage, safe team lifecycle commands, and hybrid staffing behavior.
- Keep the wrappers additive-only and resolve the real `omx` command path explicitly instead of replacing or shadowing the native `omx` executable.
- Treat verification as a leader-side native-subagent planning surface rather than a persistent verifier pane by default.
- impact_scope:
  - installer/generator
  - generated user-level PowerShell assets
  - user-level team-mode documentation
- explicit_non_goals:
  - no mixed persistent pane compose layer
  - no startup binding changes for `cmd.exe`
  - no OpenClaw runtime config changes
  - no forced persistent `verifier` pane model
- rollout_sequence:
  1. define the new user-level team entrypoint capability
  2. extend the installer and shared support script
  3. validate wrappers against a fake `omx` target in a temporary Codex home
  4. regenerate into the real user home only after repo validation passes
- rollback_plan:
  - reuse the installer transaction so new wrapper/playbook paths are included in backup snapshots and restored on failure
- validation_path:
  - PowerShell wrapper tests with a fake `omx`
  - `openspec validate --all`
  - `python .\tools\run_openspec_guard.py --root .`
- mainline_classification:
  - existing mainline: Codex / oh-my-codex user-level team mode

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-team-entrypoints`: user-level `omx team` wrappers, hybrid staffing bridge, verification planning wrapper, and generated playbook

### Modified Capabilities
- None.

## Impact

- Affected code:
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `openspec/changes/implement-codex-user-level-team-mode-p2-team-entrypoints/`
- Generated user-level assets under the target Codex home:
  - `bin/omx-team-dev.ps1`
  - `bin/omx-team-debug.ps1`
  - `bin/omx-team-verify.ps1`
  - `bin/omx-team-ops.ps1`
  - `bin/omx-team-hybrid.ps1`
  - `docs/team-mode-playbook.md`
- Systems:
  - user-level PowerShell operation for `omx team`
  - backup snapshot and rollback coverage for the new generated assets
