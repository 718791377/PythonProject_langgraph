# Delta: CLI-Anything receipt and harness-boundary guard

## ADDED Requirements

### Requirement: CLI-Anything governance guard SHALL require receipt evidence and harness-generation boundaries

The repository SHALL provide a repo-local CLI-Anything governance guard that validates install/update receipt evidence and harness-generation boundaries before any future user-level CLI-Anything or CLI Hub adaptation is treated as eligible.

The guard SHALL support at least:

- `install-record --receipt-dir <dir> --pin <pin> --install-path <path> --wrapper-path <path> --state-path <path> --smoke-command <cmd> --rollback-pointer <pointer> --json`;
- `validate --receipt <path> --json`;
- `update-plan --current-receipt <path> --new-pin <pin> --staging-dir <path> --smoke-status <status> --json`;
- `update-record --current-receipt <path> --receipt-dir <dir> --new-pin <pin> --staging-dir <path> --smoke-command <cmd> --smoke-status <status> --json`;
- `rollback-plan --receipt <path> --json` - reports rollback evidence without executing rollback;
- `harness-plan --capability <text> --output-dir <path> --target-process <process> --json` - reports harness-generation eligibility without generating or running a live harness.

The guard SHALL keep CLI-Anything as harness-generation support only until install/update receipts, smoke evidence, and rollback evidence exist. It SHALL NOT clone CLI-Anything, perform network fetches, install wrappers, run CLI-Anything, mutate user-level Codex configuration, hard-load bulk skills, control live applications, or emit raw private install/wrapper/state/output paths in default output.

#### Scenario: Pinned CLI-Anything install receipt is written without installing the tool

- **WHEN** `python tools/cli_anything_governance.py install-record --receipt-dir <tmp> --pin v0.1.0 --install-path <path> --wrapper-path <path> --state-path <path> --smoke-command "cli-anything --help" --rollback-pointer <pointer> --json` runs
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL write a `cli-anything.lock.json` receipt
- **AND** it SHALL report path hashes instead of raw private paths
- **AND** it SHALL report `installs_cli_anything=false`, `runs_cli_anything=false`, `hard_loads_skills=false`, and `harness_generation_boundary_only=true`

#### Scenario: CLI-Anything hard-load skill attempts are blocked

- **WHEN** the receipt guard is asked to write an install receipt with hard-loaded skills enabled
- **THEN** it SHALL fail closed with `hard_load_skills_must_be_false`
- **AND** no receipt SHALL be written

#### Scenario: CLI-Anything update pin switch requires smoke evidence and rollback pointer

- **WHEN** `update-plan` receives a valid current receipt but the new smoke status is not `pass`
- **THEN** it SHALL fail closed
- **AND** it SHALL report `pin_switch_allowed=false`
- **AND** it SHALL NOT perform a network fetch

- **WHEN** `update-record` receives a valid current receipt, immutable new pin, and passing smoke evidence
- **THEN** it SHALL write an update receipt
- **AND** the update receipt SHALL include previous receipt id and previous pin rollback evidence

#### Scenario: CLI-Anything harness planning remains generation-only

- **WHEN** `harness-plan --capability <text> --output-dir <path> --target-process WXWork.exe --json` runs without hard-loaded skills
- **THEN** it SHALL return `harness_generation_allowed=true`
- **AND** it SHALL report repo-local source and live-control authorization gates
- **AND** it SHALL NOT run CLI-Anything, control WXWork, hard-load skills, or emit raw private output paths

- **WHEN** `harness-plan` is asked to hard-load skills
- **THEN** it SHALL fail closed with `hard_load_skills_must_be_false`
