# codex-user-level-durable-state-cleanup-and-reconciliation Specification

## Purpose

Define a user-level contract for safely classifying, cleaning, and reconciling stale or unmanaged durable orchestration residue across repo-local backends.

## Requirements

### Requirement: The user-level workflow SHALL classify durable-state residue by cleanup safety
The user-level durable-state cleanup and reconciliation workflow SHALL classify repo-local durable-state residue by cleanup safety rather than by backend name alone.

At minimum it SHALL distinguish:

- safe cleanup candidate
- manual reconciliation required
- protected state

#### Scenario: Operator inspects empty unmanaged native team residue
- **WHEN** repo-local native durable-team residue is unmanaged and contains no files
- **THEN** the cleanup workflow SHALL classify it as a safe cleanup candidate
- **AND** it SHALL not require the operator to treat that residue as protected state

### Requirement: Safe cleanup SHALL remain narrow in the first rollout
The first rollout SHALL only treat explicitly safe residue as removable without broader manual reconciliation.

At minimum the safe cleanup set SHALL include:

- stale tracked native team record that points to a missing team directory
- empty unmanaged native team directories

#### Scenario: Tracked record points to a missing native team directory
- **WHEN** the tracked native durable-team record exists but the referenced team directory is missing
- **THEN** the cleanup workflow SHALL classify the tracked record as stale
- **AND** it SHALL allow that stale record to be cleared through the reconciliation path

### Requirement: Protected or ambiguous residue SHALL not be silently deleted
The cleanup and reconciliation workflow SHALL NOT silently remove non-empty or otherwise ambiguous durable-state residue.

Such residue SHALL be surfaced as manual-reconciliation-required or protected until the operator explicitly confirms the action or a backend-specific contract later declares it safe.

#### Scenario: Unmanaged durable residue contains non-empty state
- **WHEN** unmanaged durable-state residue contains files or otherwise appears to retain backend-specific recovery data
- **THEN** the cleanup workflow SHALL not classify it as a safe cleanup candidate
- **AND** it SHALL preserve that residue for manual inspection

### Requirement: Cleanup and reconciliation SHALL remain source-attributed
The cleanup and reconciliation workflow SHALL report which tracked records, repo-local state roots, or residue paths drove each cleanup classification or reconciliation recommendation.

#### Scenario: Operator requests a cleanup or reconciliation plan
- **WHEN** the operator requests a cleanup or reconciliation plan for repo-local durable state
- **THEN** the workflow SHALL report the residue paths or tracked records involved
- **AND** it SHALL expose enough evidence for the operator to distinguish safe cleanup from protected state

### Requirement: Cleanup and reconciliation SHALL classify stale compose runtime residue explicitly

The cleanup and reconciliation workflow SHALL classify stale compose runtime residue explicitly instead of folding it into generic unmanaged native residue.

#### Scenario: Tracked compose runtime file points to missing launched pane teams

- **WHEN** tracked compose runtime state exists but the launched pane teams it references no longer exist
- **THEN** the cleanup workflow SHALL classify that state as stale compose runtime residue
- **AND** it SHALL not present it as a healthy active compose runtime
