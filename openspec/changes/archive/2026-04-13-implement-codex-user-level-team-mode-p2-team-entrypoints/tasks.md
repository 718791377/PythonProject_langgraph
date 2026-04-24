## 1. OpenSpec Artifacts

- [x] 1.1 Create the `implement-codex-user-level-team-mode-p2-team-entrypoints` proposal, design, and capability spec.
- [x] 1.2 Record the native-`omx` preservation rule plus the new generated wrapper/playbook assets.
- [x] 1.3 Record the hybrid-staffing bridge and verification-plan semantics.

## 2. Installer / Generator

- [x] 2.1 Extend the installer to resolve a native `omx` command path and generate the new wrapper assets plus playbook.
- [x] 2.2 Extend the shared support script with team-name discovery, ops dispatch, hybrid planning, and verification planning helpers.
- [x] 2.3 Keep the new assets inside the existing additive-only backup snapshot and rollback transaction.

## 3. Validation

- [x] 3.1 Extend the PowerShell test to validate wrapper generation and command dispatch against a fake `omx` target.
- [x] 3.2 Validate `omx-team-dev`, `omx-team-debug`, `omx-team-ops`, and `omx-team-hybrid` behavior.
- [x] 3.3 Validate that `omx-team-verify` emits a leader-side verification plan instead of a persistent verifier launch.
- [x] 3.4 Run `openspec validate --all` and `python .\tools\run_openspec_guard.py --root .`.
