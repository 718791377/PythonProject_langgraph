## Why

P0 through P4 made wrapped startup, expert-routing thresholds, team entrypoints, and burst-review roles real, but durable `omx team` usage is still too manual. P5 closes the remaining gap so enhanced Codex sessions can decide when to stay subagent-only, when to start or reuse a durable team, and when to switch or stop that team without replacing native Codex.

## What Changes

- Add an automatic durable-team routing helper that can plan or apply `launch`, `reuse`, `switch`, `shutdown`, or `no-team` decisions for the current repository.
- Extend the shared user-level runtime so routing policy exposes the durable-team phase map, thresholds, tracked-team rules, and helper path in a machine-readable form.
- Extend generated leader/playbook guidance so wrapped Codex sessions know when to prefer native subagents and when to prefer the durable-team helper.
- Keep the durable-team helper additive-only, repo-scoped, and safe by default: it must not auto-adopt unmanaged existing teams and must not break native Codex startup.
- Keep startup semantics unchanged: wrapped `codex` startup still does not auto-launch a durable team on every launch; durable teams are only launched later when the leader judges the thresholds are met.
- impact_scope:
  - installer/generator
  - generated user-level PowerShell assets
  - generated leader/playbook guidance
  - repo-local `.omx` tracked team metadata
- explicit_non_goals:
  - no changes to native `codex.cmd` or native `omx.cmd`
  - no forced durable team on every `codex` start
  - no automatic adoption of unknown unmanaged teams
  - no OpenClaw runtime config changes
- rollout_sequence:
  1. define the automatic durable-team routing capability and spec deltas
  2. extend the installer and shared runtime with the new helper and tracked-team model
  3. validate launch, reuse, switch, and shutdown behavior in a temporary Codex home with a fake `omx`
  4. regenerate into the real user home only after repo validation passes
- rollback_plan:
  - keep the new helper and tracked-team-facing assets inside the existing installer backup and rollback transaction
  - on install failure, restore the previous user-level state and generated asset set from the snapshot
- validation_path:
  - PowerShell wrapper tests with a fake `omx`
  - `openspec validate --all`
  - `python .\tools\run_openspec_guard.py --root .`
- mainline_classification:
  - existing mainline: Codex / oh-my-codex user-level team mode

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-automatic-team-routing`: automatic durable-team routing helper, tracked-team metadata, and repo-safe launch or reuse or switch or shutdown behavior

### Modified Capabilities
- `codex-user-level-team-mode-routing-thresholds`: routing policy and developer instructions now expose durable-team auto-routing rules and helper usage
- `codex-user-level-team-mode-team-entrypoints`: generated user-level team entrypoints now include an automatic durable-team routing helper

## Impact

- Affected code:
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md`
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md`
  - `openspec/changes/implement-codex-user-level-team-mode-p5-automatic-team-routing/`
- Generated user-level assets under the target Codex home:
  - `bin/omx-team-auto.ps1`
  - `bin/codex-routing-policy.ps1`
  - `agents/team-leader.toml`
  - `docs/team-mode-playbook.md`
- Repo-local runtime state:
  - `.omx/state/team/codex-auto-managed-team.json`
- Systems:
  - wrapped Codex startup guidance in enhanced auto mode
  - durable-team launch, reuse, switch, and shutdown coordination across repositories
