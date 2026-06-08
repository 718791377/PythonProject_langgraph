## ADDED Requirements

### Requirement: Durable capability readiness refresh SHALL write an explicit R4 projection receipt only on request

`codex-durable-state-status.ps1` SHALL remain read-only by default and SHALL create repo-local readiness projection receipts only when the operator passes an explicit readiness refresh switch.

The receipt SHALL preserve `installed`, `enabled`, `selected`, and `ready` as distinct readiness fields for `native_omx` and `langgraph`. It SHALL include `generated_at`, source receipt evidence, selector evidence, version or install evidence, blockers, and the R4 `smoke-tested` marker. It SHALL also state that no durable workflow was adopted and no persistent team was launched by the refresh.

#### Scenario: Default status remains read-only

- **WHEN** the operator runs `codex-durable-state-status.ps1 -RepoRoot <repo> -Json`
- **AND** `<repo>` has no `.omx` directory
- **THEN** the helper SHALL report durable state and readiness without creating `.omx`
- **AND** it SHALL expose the explicit refresh command as metadata

#### Scenario: Explicit refresh writes a projection receipt

- **WHEN** the operator runs `codex-durable-state-status.ps1 -RepoRoot <repo> -RefreshReadiness -Json`
- **THEN** the helper SHALL write `<repo>/.omx/state/readiness/durable-capability-readiness-projection.json`
- **AND** the receipt SHALL contain `promotion_marker=smoke-tested`
- **AND** the receipt SHALL contain `generated_at`, `source_receipts`, `selector_evidence`, `version_evidence`, and `blockers`
- **AND** the receipt SHALL preserve distinct `installed`, `enabled`, `selected`, and `ready` fields
- **AND** the receipt SHALL report durable workflow adoption and persistent-team launch as false
