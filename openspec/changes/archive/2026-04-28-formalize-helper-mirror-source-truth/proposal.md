## Why

User-level helper scripts are shared across repositories, but the repository source and each consumer repository's `.omx/state/` directory remain the durable truth. Cold-start sessions need machine-readable and documented provenance so generated helpers are not mistaken for the source of truth or a global durable-state root.

## What Changes

- Add a helper mirror source-of-truth contract to generated user-level status surfaces.
- Expose provenance metadata that identifies generated helpers as install artifacts and points readers back to repository source.
- Add tests proving the generated durable-state status output distinguishes helper mirrors from repo-local durable truth.
- Keep all changes read-only for durable state; no `.omx/state/` activation, cleanup, or migration is performed.

## Capabilities

### New Capabilities
- `codex-user-level-helper-mirror-source-truth`: Defines provenance and source-of-truth requirements for generated user-level helper mirrors.

### Modified Capabilities
- None.

## Impact

- Impact scope: `tools/install-codex-user-level-team-mode.ps1` - repository source script that generates user-level helper scripts.
- Impact scope: `test/install-codex-user-level-team-mode.test.ps1` - installer regression test that verifies generated helper behavior.
- Impact scope: `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.*` - active rollout plan that defines MR5.
- Impact scope: OpenSpec change artifacts under `openspec/changes/formalize-helper-mirror-source-truth/`.
- Explicit non-goals: do not edit `C:\Users\lenovo\.codex\config.toml`; do not delete user-level skills; do not mutate repo-local `.omx/state/`; do not start a durable team.
- Rollout sequence: add contract artifacts, update generated helper metadata, add tests, run repository checks, then publish through GitLab-first MR.
- Rollback plan: revert this MR; generated helper behavior falls back to the previous status output without touching durable state.
- Validation path: run the installer regression test, OpenSpec validation, and repository guard checks.
- Mainline classification: existing active cross-session durable-state isolation rollout, MR5 slice.
