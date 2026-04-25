## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose graph-migration compatibility posture for tracked threads

The user-level LangGraph backend SHALL expose bounded graph-migration compatibility posture for tracked threads instead of assuming every persisted thread remains safely resumable under the latest graph contract.

At minimum the backend SHALL be able to report:

- current graph-contract identity
- tracked thread contract identity when present
- topology compatibility posture
- state-schema compatibility posture
- overall thread-compatibility verdict

#### Scenario: Operator inspects a tracked thread after the graph contract changed

- **WHEN** a tracked LangGraph thread was created under an older graph contract than the current backend contract
- **THEN** the backend SHALL preserve bounded migration and compatibility posture in durable state
- **AND** it SHALL not overstate that thread as fully resumable without compatibility classification

### Requirement: The LangGraph backend SHALL distinguish migration-safe, degraded-compatible, and incompatible thread posture

The user-level LangGraph backend SHALL distinguish at minimum:

- migration_safe
- degraded_compatible
- incompatible

#### Scenario: Operator inspects a degraded-compatible tracked thread

- **WHEN** a tracked LangGraph thread remains inspectable but not fully confidence-equivalent under the current graph contract
- **THEN** the backend SHALL classify that thread as degraded-compatible or equivalent
- **AND** it SHALL keep that posture distinct from both migration-safe and incompatible threads
