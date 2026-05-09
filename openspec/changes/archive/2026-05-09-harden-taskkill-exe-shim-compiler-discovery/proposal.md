## Why

A resumed wrapped `codex-ohmy` session still exposed localized Windows `taskkill` success lines because the user-level install did not have a generated `win-shims\taskkill.exe` shim. The installer already requested explicit `taskkill.exe` coverage, but the compilation path was not robust enough for normal Windows Framework compiler locations and sandboxed temp-file environments.

## What Changes

- Harden the user-level team-mode installer so the generated `taskkill.exe` cleanup shim can compile using Windows Framework compiler locations even when `csc.exe` is not on PATH.
- Write compiler capture files next to the generated shim instead of depending on the ambient temp directory.
- Extend the cleanup-output checker and tests so the contract covers framework compiler fallback, local compiler temp files, and Chinese `taskkill` success output suppression.
- Regenerate/install the user-level wrapper after validation so the local machine actually receives `win-shims\taskkill.exe`.
- Patch the two authorized Twilio plugin cache `SKILL.md` metadata errors as a local cache hotfix; this is not repository source truth.
- No breaking changes.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-windows-cleanup-output-control`: the explicit `taskkill.exe` shim requirement now requires robust compiler discovery and local compiler output capture so the default install can actually produce the executable shim on ordinary Windows hosts.

## Impact

- Affected source: `tools/install-codex-user-level-team-mode.ps1`.
- Affected validation: `tools/check_windows_cleanup_output_control.py` and `test/check_windows_cleanup_output_control.test.py`.
- Affected local install artifact after regeneration: `C:\Users\lenovo\.codex\bin\win-shims\taskkill.exe` plus regenerated managed wrappers.
- Affected local plugin cache hotfix: two Twilio Developer Kit `SKILL.md` files under `C:\Users\lenovo\.codex\plugins\cache\...`.

## Required Governance Fields

- impact_scope: user-level wrapped Codex startup cleanup-output control; local Twilio plugin cache metadata warning cleanup.
- explicit_non_goals: do not disable direct `omx_*` MCP entries; do not mutate `C:\Users\lenovo\.codex\config.toml`; do not remove Twilio/browser/Vercel/design skills; do not change native `codex-raw` behavior.
- rollout_sequence: source patch, focused tests, OpenSpec guard, regenerate user-level wrapper, patch authorized Twilio cache, verify installed artifacts.
- rollback_plan: rerun the previous installer version or remove only generated `win-shims\taskkill.exe` if it misbehaves; restore Twilio cache files from plugin refresh/update if local hotfix is superseded.
- validation_path: focused Python tests for cleanup-output control, installer compile smoke, repository OpenSpec guard, installed file existence and metadata validation.
- mainline_classification: existing current mainline maintenance slice under `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`.