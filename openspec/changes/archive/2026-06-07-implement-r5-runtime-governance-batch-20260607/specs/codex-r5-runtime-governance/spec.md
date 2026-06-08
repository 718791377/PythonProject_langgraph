---
change: implement-r5-runtime-governance-batch-20260607
status: archived
---

# R5 Runtime Governance Requirement Delta

## ADDED Requirements

### Requirement: R5 active-candidate receipts SHALL be script-checkable

Every user-level runtime lane that claims R5 active-candidate or bounded-live handoff SHALL provide a script-checkable receipt containing authorization, owner lease, target/action allowlist, timeout release, redaction, rollback, cleanup, lane authority, and no-remote-mutation evidence.

#### Scenario: positive R5 receipt is accepted

- **GIVEN** a receipt declares `runtime_stage` as `active-candidate`
- **AND** it includes current authorization, owner lease, allowlist, timeout release, redacted transcript, rollback-ready pointer, cleanup evidence, and no remote mutation
- **WHEN** the lane checker validates the receipt
- **THEN** it reports the receipt as accepted R5 active-candidate evidence

#### Scenario: blocked receipt does not count as active-candidate

- **GIVEN** a receipt declares blocked, dry-run, not-installed, or missing authorization state
- **WHEN** the lane checker validates the receipt
- **THEN** it may report honest blocked evidence
- **AND** it MUST NOT count that receipt as positive R5 active-candidate completion

### Requirement: Authority priority SHALL remain enforced at R5

Runtime lanes SHALL preserve the priority `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` before any R5 handoff is accepted.

#### Scenario: subordinate authority is blocked

- **GIVEN** a gstack, harness, or Spec Kit receipt attempts to override a higher-priority authority layer
- **WHEN** the checker evaluates the receipt
- **THEN** it fails with a named authority-priority error
