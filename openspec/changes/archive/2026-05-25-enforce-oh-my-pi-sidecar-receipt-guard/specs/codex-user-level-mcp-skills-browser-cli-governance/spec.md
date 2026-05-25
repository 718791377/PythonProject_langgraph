# Delta: oh-my-pi sidecar receipt guard

## ADDED Requirements

### Requirement: oh-my-pi sidecar receipt guard SHALL require pinned smoke-tested rollback evidence

The repository SHALL provide a repo-local `oh-my-pi` sidecar governance guard
that validates install/update receipt evidence before any future user-level
`oh-my-pi` sidecar installation or update is treated as eligible.

The guard SHALL support at least:

- `install-record --receipt-dir <dir> --pin <pin> --install-path <path> --wrapper-path <path> --state-path <path> --smoke-command <cmd> --rollback-pointer <pointer> --json`;
- `validate --receipt <path> --json`;
- `update-plan --current-receipt <path> --new-pin <pin> --staging-dir <path> --smoke-status <status> --json`;
- `update-record --current-receipt <path> --receipt-dir <dir> --new-pin <pin> --staging-dir <path> --smoke-command <cmd> --smoke-status <status> --json`;
- `rollback-plan --receipt <path> --json` - reports rollback evidence without executing rollback.

The guard SHALL NOT clone `oh-my-pi`, perform network fetches, install wrappers,
run the sidecar, mutate user-level Codex configuration, hard-load skills, or
emit raw private install/wrapper/state paths in default output.

#### Scenario: Pinned install receipt is written without installing the sidecar

- **WHEN** `python tools/oh_my_pi_sidecar_governance.py install-record --receipt-dir <tmp> --pin v0.4.2 --install-path <path> --wrapper-path <path> --state-path <path> --smoke-command "oh-my-pi --help" --rollback-pointer <pointer> --json` runs
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL write an `oh-my-pi.lock.json` receipt
- **AND** it SHALL report path hashes instead of raw private paths
- **AND** it SHALL report `installs_oh_my_pi=false`, `runs_oh_my_pi=false`, and `hard_loads_skills=false`

#### Scenario: Unpinned refs are blocked

- **WHEN** the receipt guard is asked to record `main`, `master`, `HEAD`, `latest`, or a branch ref as the pin
- **THEN** it SHALL fail closed with `pin_must_be_immutable`
- **AND** no receipt SHALL be written

#### Scenario: Update pin switch requires smoke evidence and rollback pointer

- **WHEN** `update-plan` receives a valid current receipt but the new smoke status is not `pass`
- **THEN** it SHALL fail closed
- **AND** it SHALL report `pin_switch_allowed=false`
- **AND** it SHALL NOT perform a network fetch

- **WHEN** `update-record` receives a valid current receipt, immutable new pin, and passing smoke evidence
- **THEN** it SHALL write an update receipt
- **AND** the update receipt SHALL include previous receipt id and previous pin rollback evidence

#### Scenario: Rollback remains planned and operator-executed

- **WHEN** `rollback-plan --receipt <update-receipt> --json` runs against a valid update receipt
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL expose the sanitized rollback pointer
- **AND** it SHALL report `rollback_performed=false`
- **AND** it SHALL require operator execution for any actual rollback
