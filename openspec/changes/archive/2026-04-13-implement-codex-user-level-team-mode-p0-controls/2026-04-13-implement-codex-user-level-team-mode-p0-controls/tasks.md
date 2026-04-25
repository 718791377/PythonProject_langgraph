## 1. OpenSpec Artifacts

- [x] 1.1 Create the `implement-codex-user-level-team-mode-p0-controls` proposal, design, and capability spec.
- [x] 1.2 Capture the P0 boundary: additive user-level control assets only, with no native `codex` replacement.
- [x] 1.3 Record separate `oh_my_codex` and `subagent_routing` control semantics plus pure debugging mode.

## 2. Installer / Generator

- [x] 2.1 Add a repo-local installer that renders the P0 control assets into an explicit target Codex home.
- [x] 2.2 Generate the shared support script, leader profile, state file, and wrapper scripts for omx and routing control.
- [x] 2.3 Reject unmanaged collisions by default and preserve native `codex`-named files.
- [x] 2.4 Create timestamped backup snapshots before writes and restore managed paths automatically on install failure.

## 3. Validation

- [x] 3.1 Add a dedicated PowerShell test that validates generation, state transitions, and unmanaged-collision rejection.
- [x] 3.2 Validate pure debugging mode semantics and additive-only safety guarantees.
- [x] 3.3 Validate backup snapshot creation plus rollback of partially applied installs.
- [x] 3.4 Run `openspec validate --all` and `python .\tools\run_openspec_guard.py --root .`.
