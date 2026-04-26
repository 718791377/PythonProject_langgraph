## ADDED Requirements

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
