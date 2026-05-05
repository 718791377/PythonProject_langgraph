## Why

The current user-level team-mode baseline already protects native Codex conceptually and the installer has backup and rollback behavior. What is still missing is a release-level gate that makes those protections explicit before any release is marked production-ready.

The user requirement is that Codex native functionality must remain available, a release must be recoverable, and daily Codex use must not be broken by the wrapper or user-level team-mode assets.

## What Changes

- Add a Codex native preservation and rollback release-gate template.
- Add a repository checker that validates the release-gate template and static source evidence.
- Wire the checker into `tools/run_openspec_guard.py` - the repository OpenSpec guard that aggregates project enforcement checks.
- Extend the active team-mode plan and the long-term production durable-team draft with the release-gate slice.

## Capabilities

### New Capabilities

- `codex-user-level-team-mode-controls` - adds a release gate for native Codex preservation, backup snapshots, rollback evidence, and config rewrite sentinel evidence.
- `codex-user-level-team-mode-startup-binding` - adds startup-binding release checks for `codex`, `codex-raw`, and `codex-ohmy` entrypoint behavior.

### Modified Capabilities

- None.

## Impact

- Affected paths:
  - `tools/codex_native_rollback_release_gate_template.json` - JSON template describing required release evidence for native Codex preservation and rollback.
  - `tools/check_codex_native_rollback_release_gate_template.py` - static checker that validates the release-gate template and repository evidence.
  - `tools/run_openspec_guard.py` - aggregate guard that will run the new checker.
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - active English implementation plan for user-level team mode.
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` - Chinese companion implementation plan for user-level team mode.
  - `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` - English draft of the long-term production durable-team target.
  - `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` - Chinese companion draft of the long-term production durable-team target.
- This change does not install or activate user-level assets.
- This change does not modify `C:\Users\lenovo\.codex\config.toml` - the Codex user configuration file that must remain under explicit operator control.
- This change does not replace the native `codex` executable or launch any durable team.

## impact_scope

- repository-local release-gate template and checker only
- static source evidence for native Codex preservation and rollback behavior
- OpenSpec guard integration
- bilingual plan alignment for the new release slice

## explicit_non_goals

- no live installation into the real user Codex home
- no mutation of `C:\Users\lenovo\.codex\config.toml` - the Codex user configuration file
- no replacement, wrapping, or modification of `codex`, `codex.cmd`, or `codex.ps1` - native Codex entrypoint names
- no durable-team launch, no `omx team`, and no LangGraph runtime activation
- no GitLab or GitHub publication action in this change itself

## rollout_sequence

1. Define the release-gate template.
2. Add the checker for required release evidence and static source evidence.
3. Wire the checker into the OpenSpec guard.
4. Update the active plan and long-term draft with the release-gate slice.
5. Validate with the checker, OpenSpec validation, installer rollback test, and the aggregate guard.

## rollback_plan

- Remove the new template and checker if the release gate proves too broad or misleading.
- Remove the new guard step from `tools/run_openspec_guard.py` - the aggregate OpenSpec guard script.
- Revert only repository-local files; no user-level Codex assets are changed by this slice.

## validation_path

- Run `python .\tools\check_codex_native_rollback_release_gate_template.py --root . --json` - validates the release-gate template and static repository evidence.
- Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\test\install-codex-user-level-team-mode.test.ps1` - validates installer backup and rollback behavior in temporary directories.
- Run `openspec validate --all` - validates OpenSpec artifacts and stable specs.
- Run `python .\tools\run_openspec_guard.py --root . --tool codex --json` - runs the aggregate repository guard.
- Optionally run local smoke checks `codex --version`, `codex-raw --version`, and a short `codex-ohmy` help/version check before production publication.

## mainline_classification

- bounded release-gate hardening slice
- no runtime activation
- safe to implement before later native_omx or LangGraph adoption work
