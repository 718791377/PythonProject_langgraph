## ADDED Requirements

### Requirement: OpenCLI live-start preflight SHALL require install receipt, owner evidence, and port lease evidence

The repository-local OpenCLI governance guard SHALL provide a non-mutating live-start preflight that fails closed unless OpenCLI has valid install receipt evidence, active browser-owner lease evidence, and sanitized codex-port `--port auto` lease evidence in the Codex browser/OpenCLI range.

Even when all evidence is present, the repo-local MVP SHALL NOT start OpenCLI. It SHALL return `live_start_not_implemented_repo_local_mvp` and `start_performed=false`.

#### Scenario: OpenCLI live start lacks install receipt

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> --owner-state-dir <owner-state> start --target tab:opencli-1 --session session-a --owner-lease-id <lease> --port-lease-receipt <receipt> --json` runs without an install receipt
- **THEN** the command SHALL fail closed
- **AND** it SHALL include `install_receipt_required` in blockers
- **AND** it SHALL report `start_performed=false`

#### Scenario: OpenCLI live start lacks owner evidence

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> start --target tab:opencli-1 --session session-a --install-receipt <receipt> --port-lease-receipt <receipt> --json` runs without owner evidence
- **THEN** the command SHALL fail closed
- **AND** it SHALL include `owner_lease_required` in blockers
- **AND** it SHALL report `install_receipt_verified=true`

#### Scenario: OpenCLI live start has complete evidence but remains deferred

- **WHEN** the OpenCLI live-start preflight receives valid install receipt, owner lease, and port lease evidence
- **THEN** the command SHALL fail closed with `live_start_not_implemented_repo_local_mvp`
- **AND** it SHALL report `start_performed=false`
- **AND** it SHALL NOT install OpenCLI, start OpenCLI, launch browsers, connect to browser targets, or mutate user-level Codex configuration
