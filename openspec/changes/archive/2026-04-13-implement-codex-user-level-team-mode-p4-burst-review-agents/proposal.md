## Why

P3 made the routing thresholds inspectable, but the strongest execution-loop branch is still incomplete: `bug-finder`, `bug-rebutter`, and `bug-judge` exist only as documented routing concepts, not as real user-level callable roles.

The next gap is to turn that documented adversarial review flow into additive, installable, and verifiable user-level agent assets so Codex CLI can route into them when thresholds say they are needed.

## What Changes

- Generate additive user-level agent profiles for:
  - `agents/bug-finder.toml`
  - `agents/bug-rebutter.toml`
  - `agents/bug-judge.toml`
- Extend the generated routing-policy surface so it reports the burst-review roles as callable generated assets instead of only abstract names.
- Update generated `team-leader.toml` and `docs/team-mode-playbook.md` so they describe the burst-review triad as real leader-side callable roles.
- Keep the new agent profiles inside the existing backup snapshot and rollback-on-error transaction.
- Extend the PowerShell installer test so it validates generation, manifest coverage, rollback behavior, and routing-policy visibility for the burst-review roles.
- impact_scope:
  - installer/generator
  - generated user-level agent assets
  - generated routing-policy output
  - generated leader profile and playbook
  - wrapper-validation test coverage
- explicit_non_goals:
  - no mixed persistent pane compose layer
  - no auto-launch of burst-review roles on normal `codex` startup
  - no durable bug-review swarm
  - no replacement of native `codex` or native `omx`
  - no OpenClaw runtime config changes
- rollout_sequence:
  1. define the burst-review role capability and the routing-policy delta
  2. extend the installer with generated burst-review agent profiles
  3. extend the shared support script, leader profile, and playbook with callable burst-role metadata
  4. validate generation and rollback in a temporary Codex home
  5. reinstall into the real user home only after repository validation passes
- rollback_plan:
  - reuse the installer transaction so the new agent files and updated generated assets are restored on failure
- validation_path:
  - PowerShell installer test with fake native Codex and fake `omx`
  - real user-level `omx agents list --scope user`
  - `openspec validate --all`
  - `python .\tools\run_openspec_guard.py --root .`
- mainline_classification:
  - existing mainline: Codex / oh-my-codex user-level team mode

## Capabilities

### New Capabilities

- `codex-user-level-team-mode-burst-review-agents`: generated user-level bug-finder, bug-rebutter, and bug-judge profiles for leader-side adversarial review bursts

### Modified Capabilities

- `codex-user-level-team-mode-routing-thresholds`: routing-policy output and generated guidance must describe the burst-review triad as real callable generated roles when installed

## Impact

- Affected code:
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `openspec/changes/implement-codex-user-level-team-mode-p4-burst-review-agents/`
- Generated user-level assets under the target Codex home:
  - `agents/bug-finder.toml`
  - `agents/bug-rebutter.toml`
  - `agents/bug-judge.toml`
  - `bin/_codex-user-level-team-mode.ps1`
  - `bin/codex-routing-policy.ps1`
  - `agents/team-leader.toml`
  - `docs/team-mode-playbook.md`
- Systems:
  - user-level burst-review role availability for wrapped `codex` sessions
  - operator-visible routing-policy inspection
  - backup snapshot and rollback coverage for the new generated agent assets
