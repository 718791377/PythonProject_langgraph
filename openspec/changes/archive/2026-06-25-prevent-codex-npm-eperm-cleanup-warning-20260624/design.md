---
change_id: prevent-codex-npm-eperm-cleanup-warning-20260624
status: proposed
owner: codex
created_at: 2026-06-24
archived-with: 2026-06-25-prevent-codex-npm-eperm-cleanup-warning-20260624
status: final
---

# Design: Official Update Windows Lock Preflight

## Boundary

`tools/codex-official-update-patch-replay-template.ps1` is the only implementation entrypoint for this change. It already owns the official npm update lane and emits `report.json`, `checkpoint.json`, `checklist.md`, and patch decision tables. The stable `codex-ohmy` and `codex-raw` wrappers remain thin launcher surfaces and must not receive update orchestration logic.

## Runtime Behavior

The update template adds a Windows-only preflight that runs before the official npm update whenever the selected stage or switches would run `npm install -g @openai/codex oh-my-codex`.

The preflight determines:

- the npm global root using `npm root -g` when available;
- the probable `@openai` package root under the npm global root;
- leftover `.codex-*` staging candidates under that package root;
- active process candidates whose process name or executable/command path indicates `codex.exe`, `node.exe`, or npm package execution under the global `@openai/codex` package tree.

If the platform is Windows and matching process candidates are found, the update stage fails before running npm unless `-AllowLockedCodexUpdate` is provided. With the override, the script continues and records that the override was used.

## Report Surface

The script adds `windows_codex_lock_preflight` to `report.json` and checkpoint data:

- `platform` - the runtime platform string.
- `checked` - whether the preflight ran.
- `blocking_enabled` - whether lock findings block npm update.
- `lock_risk` - preflight verdict field; `detected` means likely active process locks exist, `clear` means no likely lock holders were found, and `unknown` means process or npm-root inventory failed and manual review is required.
- `matched_processes` - bounded process evidence with PID, name, optional path, and match reason.
- `npm_global_root` - the detected npm global root when available.
- `openai_codex_package_root` - the expected package root when derivable.
- `leftover_staging_candidates` - `.codex-*` directory candidates reported but not deleted.
- `recommended_action` - `close_codex_sessions_then_rerun`, `safe_to_update`, or `manual_review`.
- `override_used` - whether `-AllowLockedCodexUpdate` bypassed blocking.

The script also adds `official_update_cleanup_warnings` to classify npm output. `windows_file_lock_eperm` is non-fatal only when the npm command exit code is zero. A non-zero npm install remains a failed update even if the output contains EPERM cleanup text.

## Testability

Tests must not depend on real machine process state. The script supports a test-only fake process inventory through an environment variable containing JSON. Production behavior falls back to real process enumeration. Fake npm commands in `test/codex-official-update-patch-replay-template.test.ps1` simulate:

- npm install success with EPERM cleanup warning;
- npm install failure with the same warning;
- npm global root discovery;
- leftover staging directories under a temporary fake npm root.

## Safety

- The script never kills processes.
- The script never deletes `.codex-*` directories by default.
- The script preserves existing `SupportsShouldProcess` and stage-gate behavior.
- The script treats process enumeration failures as `unknown` and gives manual-review guidance rather than assuming safe execution.
- The implementation remains local-main-first and stops before remote publication.
