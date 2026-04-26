## ADDED Requirements

### Requirement: The inspectable durable-state surface SHALL distinguish preserved legacy artifacts from active scoped activation
The canonical inspectable durable-state surface SHALL distinguish preserved legacy durable artifacts from active scoped activation state instead of collapsing both into one tracked-active interpretation.

At minimum it SHALL be able to distinguish:

- active scoped activation
- preserved legacy artifact state
- safe empty residue
- protected manual residue

#### Scenario: Repository has preserved legacy LangGraph state but no active scoped selector
- **WHEN** the current repository contains a preserved legacy LangGraph backend record and related artifact files
- **AND** no scoped activation selector declares that record active for the current future session
- **THEN** the inspectable surface SHALL classify that LangGraph state as preserved legacy artifact state or equivalent
- **AND** it SHALL not report that state as the active future-session durable selector

### Requirement: The inspectable durable-state surface SHALL source-attribute activation and artifact planes separately
The canonical inspectable durable-state surface SHALL source-attribute activation-plane evidence separately from artifact-plane evidence when both are present.

#### Scenario: Scoped activation coexists with preserved legacy artifacts
- **WHEN** scoped activation state exists for the current future session
- **AND** preserved legacy durable artifact state also exists in the same repository
- **THEN** the inspectable surface SHALL identify which sources came from the activation plane and which came from the legacy artifact plane
- **AND** it SHALL not force the operator to infer active-versus-preserved state only from raw file names
