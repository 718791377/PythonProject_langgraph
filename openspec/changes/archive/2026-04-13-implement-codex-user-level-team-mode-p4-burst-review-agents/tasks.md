## 1. OpenSpec Artifacts

- [x] 1.1 Create the `implement-codex-user-level-team-mode-p4-burst-review-agents` proposal, design, and capability specs.
- [x] 1.2 Record the generated burst-review agent profiles and the read-only leader-side usage rule.
- [x] 1.3 Record the routing-policy delta that exposes installed callable burst-review roles.

## 2. Installer / Generator

- [x] 2.1 Extend the installer to generate `bug-finder.toml`, `bug-rebutter.toml`, and `bug-judge.toml` into the target user-level `agents/` directory.
- [x] 2.2 Extend the shared support runtime and `codex-routing-policy.ps1` output with installed burst-role metadata and callable-role visibility.
- [x] 2.3 Update generated `team-leader.toml` and `docs/team-mode-playbook.md` so they describe the burst-review triad as real generated leader-side roles.
- [x] 2.4 Keep the new agent files inside the existing additive-only backup snapshot and rollback transaction.

## 3. Validation

- [x] 3.1 Extend the PowerShell installer test to validate burst-role file generation and backup-manifest coverage.
- [x] 3.2 Validate rollback behavior for fresh-install and existing-install failure paths with the new agent files.
- [x] 3.3 Validate `codex-routing-policy.ps1 -Json` exposes the installed burst-review roles.
- [x] 3.4 Run `test/install-codex-user-level-team-mode.test.ps1`.
- [x] 3.5 Run `openspec validate --all` and `python .\tools\run_openspec_guard.py --root .`.
- [x] 3.6 Reinstall into the real user Codex home and verify `omx agents list --scope user` shows `bug-finder`, `bug-rebutter`, and `bug-judge`.
