## 1. OpenSpec Artifacts

- [x] 1.1 Create the `implement-codex-user-level-team-mode-p1-startup-binding` proposal, design, and capability spec.
- [x] 1.2 Record the PowerShell-only startup-binding scope and the native-executable preservation rule.
- [x] 1.3 Record launcher-side state-to-args mapping plus profile rollback requirements.

## 2. Installer / Generator

- [x] 2.1 Extend the installer to generate a startup-binding launcher script and preserve the resolved native Codex path.
- [x] 2.2 Extend the installer to manage a PowerShell profile block that defines wrapped `codex` plus `codex-native`.
- [x] 2.3 Extend backup snapshot and rollback coverage to the profile path and startup-binding assets.

## 3. Validation

- [x] 3.1 Extend the PowerShell test to validate profile-block installation and launcher argument mapping using a fake native Codex target.
- [x] 3.2 Validate `oh_my_codex` and `subagent_routing` mode mapping for wrapped launches.
- [x] 3.3 Validate rollback of partial startup-binding failure.
- [x] 3.4 Run `openspec validate --all` and `python .\tools\run_openspec_guard.py --root .`.
