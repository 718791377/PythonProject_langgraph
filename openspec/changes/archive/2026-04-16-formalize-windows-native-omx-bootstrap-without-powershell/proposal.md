## Why

The native Windows `native_omx` lane now routes correctly under the user-level capability-switch model, but its success still depends on a manual hotfix applied to the globally installed `oh-my-codex` runtime. The current upstream Windows worker bootstrap uses `spawnSync('powershell.exe', ...)`, and in this environment Node cannot spawn `powershell.exe` or `cmd.exe` without hitting `EPERM`, so the repair needs to become a formal, repeatable, repo-managed solution rather than a one-off global patch.

## What Changes

- Formalize the Windows native `omx` prompt-worker bootstrap fix so it no longer depends on `powershell.exe`.
- Define the supported Windows bootstrap contract as direct Node-based worker-controller launch rather than PowerShell-mediated process creation.
- Define how the repository should install, reapply, or verify that fix against the global `oh-my-codex` runtime after upgrades.
- Add regression validation that distinguishes the old PowerShell-blocked path from the fixed Node bootstrap path.

## Capabilities

### New Capabilities
- `codex-user-level-windows-native-omx-bootstrap-fix`: a repo-managed Windows bootstrap repair path for native `omx` prompt workers that bypasses PowerShell-mediated controller startup

### Modified Capabilities
- `codex-user-level-team-mode-windows-native-team-backend`: refine the Windows backend contract so prompt-worker bootstrap does not depend on `powershell.exe`
- `codex-user-level-team-mode-automatic-team-routing`: ensure worker-centric native_omx launches remain valid after the formalized Windows bootstrap repair path is applied

## Impact

- impact_scope:
  - repo-managed repair documentation and/or scripts for the globally installed `oh-my-codex` runtime
  - Windows native `native_omx` bootstrap behavior
  - user-level validation for worker-centric durable launches
- explicit_non_goals:
  - no new backend family
  - no removal of LangGraph support
  - no redesign of the user-level capability-switch model
- rollout_sequence:
  - define the formal Windows bootstrap repair contract
  - decide where the repo-managed repair should live
  - validate that worker-centric native_omx launches succeed without PowerShell bootstrap
  - keep upgrade/reinstall survivability explicit
- rollback_plan:
  - restore the backed-up global runtime file if the repaired bootstrap path fails
  - keep the repo-managed repair assets reversible
- validation_path:
  - verify the old PowerShell bootstrap reproduces the EPERM failure
  - verify the fixed Node bootstrap path launches a native_omx team successfully
  - run `openspec validate --all`
- mainline_classification:
  - existing mainline continuation
  - specifically a user-level Windows native_omx bootstrap hardening and formalization pass
