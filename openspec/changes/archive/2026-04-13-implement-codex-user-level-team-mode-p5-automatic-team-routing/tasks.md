## 1. OpenSpec Artifacts

- [x] 1.1 Create the `implement-codex-user-level-team-mode-p5-automatic-team-routing` proposal, design, and capability specs.
- [x] 1.2 Record the automatic durable-team routing rules, tracked-team safety boundary, and helper surface.
- [x] 1.3 Record the spec deltas for routing policy and team entrypoints.

## 2. Installer / Generator

- [x] 2.1 Extend the installer and shared runtime with automatic durable-team routing thresholds and tracked-team metadata helpers.
- [x] 2.2 Generate `omx-team-auto.ps1` as the reusable plan or apply durable-team helper.
- [x] 2.3 Update generated routing policy, leader profile, playbook, and install manifest to expose the new helper and routing semantics.

## 3. Validation

- [x] 3.1 Extend the PowerShell test with a richer fake `omx` so launch, reuse, switch, and shutdown can be validated.
- [x] 3.2 Validate safe behavior when no tracked team exists, when a tracked team matches, and when an unmanaged team already exists.
- [x] 3.3 Run `openspec validate --all` and `python .\tools\run_openspec_guard.py --root .`.
