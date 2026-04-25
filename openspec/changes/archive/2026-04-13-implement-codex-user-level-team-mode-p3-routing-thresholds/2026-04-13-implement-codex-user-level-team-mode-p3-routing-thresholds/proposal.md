## Why

P2 made user-level team entrypoints real, but the leader-side role-routing policy is still too implicit. The next gap is a reusable, inspectable routing-threshold layer that keeps native Codex as the base path, makes wrapped `codex` startup behavior explicit, and lets normal projects reuse the same automatic expert-selection rules without repository-specific glue.

## What Changes

- Add a shared user-level routing-policy model to the generated support script.
- Generate a user-level `codex-routing-policy.ps1` inspection entrypoint.
- Make the startup launcher derive developer instructions from the routing-policy model instead of a short hard-coded summary.
- Expand generated `team-leader.toml` and `docs/team-mode-playbook.md` with routing thresholds, research-to-implementation handoff rules, adversarial bug-review rules, startup-path semantics, and repository-scoped runtime isolation notes.
- Keep the new routing-policy asset inside the existing additive-only backup snapshot and rollback transaction.
- Extend the PowerShell test to validate routing-policy output and injected developer instructions across `auto`, `manual`, and `off` routing states.
- impact_scope:
  - installer/generator
  - generated user-level PowerShell assets
  - generated user-level leader profile and playbook
  - wrapper-validation test coverage
- explicit_non_goals:
  - no new persistent-pane compose layer
  - no automatic durable-team launch on every `codex` start
  - no project-scoped global switch
  - no OpenClaw runtime config changes
- rollout_sequence:
  1. define the routing-threshold capability and inspection surface
  2. extend the shared support script and launcher generation
  3. extend generated leader/playbook assets
  4. validate policy output and developer-instruction injection in a temporary Codex home
  5. reinstall into the real user home only after repository validation passes
- rollback_plan:
  - reuse the installer transaction so the new routing-policy script and updated generated assets are restored on failure
- validation_path:
  - PowerShell installer test with fake native Codex and fake `omx`
  - `openspec validate --all`
  - `python .\tools\run_openspec_guard.py --root .`
- mainline_classification:
  - existing mainline: Codex / oh-my-codex user-level team mode

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-routing-thresholds`: inspectable routing policy, startup-mode-aware developer instruction generation, and generated leader/playbook updates for role-routing thresholds

### Modified Capabilities
- None.

## Impact

- Affected code:
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `openspec/changes/implement-codex-user-level-team-mode-p3-routing-thresholds/`
- Generated user-level assets under the target Codex home:
  - `bin/codex-routing-policy.ps1`
  - `bin/_codex-user-level-team-mode.ps1`
  - `bin/_codex-user-level-team-mode-launcher.ps1`
  - `agents/team-leader.toml`
  - `docs/team-mode-playbook.md`
- Systems:
  - user-level startup behavior for wrapped `codex`
  - operator-visible routing-policy inspection
  - user-level role-routing documentation and validation
