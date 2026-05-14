## MODIFIED Requirements

### Requirement: Orchestration enforcement checkers are wired into shared CI

The repository SHALL run existing automatic-orchestration enforcement checker tests through the shared local/remote CI manifest, and SHALL run no-input orchestration guard checks from `tools/run_openspec_guard.py` when they can execute without synthetic task evidence.

#### Scenario: Local gate covers existing orchestration checker tests

- **GIVEN** `tools/ci/local_gate.ps1` is run
- **WHEN** it executes Python unit tests through `tools/ci/ci_test_manifest.json`
- **THEN** capability-switch, orchestration trace evidence, expert lifecycle/wait pacing, and custom-agent TOML schema tests are included in the manifest.

#### Scenario: OpenSpec guard runs capability-switch chain validation

- **GIVEN** `tools/run_openspec_guard.py --root . --json` is run
- **WHEN** user-level capability state and repo-local backend context are available or absent
- **THEN** `check_capability_switch_chain.py` is invoked as an OpenSpec guard step and reports violations or warnings through the guard payload.
