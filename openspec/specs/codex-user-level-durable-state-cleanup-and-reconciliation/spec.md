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

### Requirement: Cleanup and reconciliation SHALL preserve legacy durable artifacts during scoped-activation rollout
During the first rollout of session-scoped durable activation, cleanup and reconciliation SHALL preserve legacy durable artifacts unless they already belong to an explicitly safe cleanup class.

Legacy preserved artifact state SHALL NOT be reclassified as safe cleanup only because it is no longer the activation truth for future sessions.

#### Scenario: Preserved legacy LangGraph backend record exists without active scoped selector
- **WHEN** a repository contains a preserved legacy LangGraph backend record
- **AND** that record is not declared active by the scoped activation plane for the current future session
- **THEN** cleanup and reconciliation SHALL preserve that record as legacy artifact state
- **AND** it SHALL not classify that record as safe cleanup only because activation has moved elsewhere

### Requirement: Cleanup and reconciliation SHALL keep empty unmanaged native residue safe but non-blocking
Cleanup and reconciliation SHALL continue classifying empty unmanaged native residue as a safe cleanup candidate, but that classification SHALL remain distinct from active blocking residue.

#### Scenario: Operator inspects empty unmanaged native residue during scoped-activation rollout
- **WHEN** repo-local native durable-team residue is unmanaged and contains no files during the scoped-activation rollout
- **THEN** cleanup and reconciliation SHALL continue to classify it as a safe cleanup candidate
- **AND** it SHALL preserve that classification distinctly from protected or active durable state

### Requirement: Legacy durable residue classification SHALL be inspectable and non-adopting
The cleanup and reconciliation workflow SHALL expose a read-only classification surface for repo-local legacy durable residue under `.omx/state/`.

At minimum, each classification record SHALL include:

- `kind` - stable residue class.
- `path` - source path for the residue or authority record.
- `state_class` - safety grouping for cleanup or inspection.
- `safe_next_action` - operator-safe next action.
- `auto_adopt_allowed` - whether this record can authorize adoption by itself.
- `reason` - source-attributed explanation.

For the first rollout, unmanaged residue and selector evidence SHALL NOT authorize automatic adoption by itself; their `auto_adopt_allowed` value SHALL be false.

#### Scenario: Legacy residue scan sees unmanaged native and completed LangGraph state
- **WHEN** repo-local `.omx/state/` contains a non-empty unmanaged native team directory
- **AND** it contains a completed LangGraph backend/thread record
- **THEN** the classification output SHALL report the unmanaged native directory as protected residue with `manual-inspection-required`
- **AND** it SHALL report the completed LangGraph state as inspect-or-archive evidence that must not be auto-resumed
- **AND** neither record SHALL allow automatic adoption by itself

#### Scenario: Legacy residue scan sees stale and current selectors
- **WHEN** `.omx/state/selectors/active.json` points to a different repository root
- **THEN** the classification output SHALL classify it as a stale selector with a refresh-or-ignore safe next action
- **AND** it SHALL not treat that selector as current adoption authority

- **WHEN** `.omx/state/selectors/active.json` points to the current repository root or omits a conflicting repository root
- **THEN** the classification output SHALL classify it as active current selector authority evidence
- **AND** it SHALL still not allow automatic adoption by that record alone
