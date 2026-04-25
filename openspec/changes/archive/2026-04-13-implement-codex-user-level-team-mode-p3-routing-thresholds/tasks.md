## 1. OpenSpec Artifacts

- [x] 1.1 Create the `implement-codex-user-level-team-mode-p3-routing-thresholds` proposal, design, and capability spec.
- [x] 1.2 Record the startup-path semantics, repository-scoped runtime isolation rule, and role-routing thresholds.
- [x] 1.3 Record the read-only routing-policy inspection surface and the non-goal that normal `codex` startup must not auto-launch a durable team.

## 2. Installer / Generator

- [x] 2.1 Extend the generated shared support script with structured routing-policy definitions, developer-instruction rendering, and startup-argument helpers.
- [x] 2.2 Generate `codex-routing-policy.ps1` and update the launcher to derive developer instructions from the shared routing-policy model.
- [x] 2.3 Update generated `team-leader.toml` and `docs/team-mode-playbook.md` so they mirror the approved routing thresholds and startup/isolation semantics.
- [x] 2.4 Keep the new routing-policy asset and updated generated files inside the existing additive-only backup snapshot and rollback transaction.

## 3. Validation

- [x] 3.1 Extend the PowerShell test to validate `codex-routing-policy.ps1` generation and JSON output.
- [x] 3.2 Validate injected developer instructions for `auto`, `manual`, and `off` routing states.
- [x] 3.3 Validate that the generated playbook and leader profile include the routing-threshold and startup-path rules.
- [x] 3.4 Run `openspec validate --all` and `python .\tools\run_openspec_guard.py --root .`.
