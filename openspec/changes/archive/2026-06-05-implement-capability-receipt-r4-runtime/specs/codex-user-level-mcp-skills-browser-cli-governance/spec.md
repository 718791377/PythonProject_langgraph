## ADDED Requirements

### Requirement: Receipt governance helper SHALL validate R4 smoke-tested receipts

The repository-local receipt governance helper SHALL provide a read-only R4 smoke receipt validation surface for user-level runtime promotion lanes.

A valid R4 smoke receipt SHALL include tool identity, owner lane, runtime stage `R4` or `smoke-tested`, prior install receipt evidence, bounded read-only smoke command evidence, passing smoke result, timeout release evidence, rollback pointer, rollback readiness, transcript redaction evidence, and redaction status. The helper SHALL emit hash-first summaries for receipt references, transcripts, and rollback pointers by default.

The helper SHALL fail closed when a smoke receipt attempts to represent write-capable behavior, R5 live handoff, sensitive action execution, raw browser data reads, external message sends, or user-level state mutation.

#### Scenario: Valid R4 smoke receipt is accepted without raw private paths

- **GIVEN** a smoke receipt records R4 or `smoke-tested` stage evidence for a bounded help/status/version/safe-discovery/read-only command
- **WHEN** `python tools/user_level_receipt_governance.py smoke-check --receipt <path> --json` runs
- **THEN** the command SHALL report `ok=true`, `smoke_receipt_valid=true`, `runtime_stage=R4`, and `rollback_ready=true`
- **AND** default output SHALL include hashes instead of raw install receipt paths, transcript contents, or rollback pointers
- **AND** the command SHALL report that it does not mutate user-level state, run external tools, or read browser data.

#### Scenario: R4 smoke receipt attempts live or write behavior

- **GIVEN** a smoke receipt marks write behavior, live action, sensitive action execution, or user-level mutation
- **WHEN** the smoke receipt checker runs
- **THEN** the command SHALL fail closed with sanitized blocker codes
- **AND** it SHALL NOT treat the lane as `smoke-tested`.

### Requirement: Receipt governance helper SHALL validate rollback executor receipts without executing rollback

The repository-local receipt governance helper SHALL validate rollback executor receipts for dry-run and apply evidence without executing rollback commands.

A rollback receipt SHALL include rollback target, rollback pointer, rollback mode, restore command evidence, dry-run result, post-rollback verification evidence, owner lane, operator authorization status, and redaction status. Apply-mode receipts SHALL fail closed unless operator authorization is explicit.

#### Scenario: Rollback apply receipt lacks operator authorization

- **GIVEN** a rollback receipt requests apply mode without explicit operator authorization
- **WHEN** `python tools/user_level_receipt_governance.py rollback-check --receipt <path> --json` runs
- **THEN** the command SHALL fail closed
- **AND** it SHALL report `rollback_performed=false` because the helper validates receipts only and never executes rollback commands.
