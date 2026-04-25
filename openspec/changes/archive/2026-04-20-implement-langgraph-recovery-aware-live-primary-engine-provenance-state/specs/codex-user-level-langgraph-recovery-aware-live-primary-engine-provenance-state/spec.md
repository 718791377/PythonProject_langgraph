## ADDED Requirements

### Requirement: The user-level LangGraph lane SHALL expose recovery-aware live primary-engine provenance-state semantics as an additive durable capability

The user-level LangGraph durable lane SHALL expose recovery-aware live primary-engine provenance-state semantics as an additive durable capability under the existing Codex CLI leader model.

#### Scenario: Operator inspects the user-level recovery-aware provenance-state live-engine capability

- **WHEN** the operator inspects the user-level LangGraph recovery-aware provenance-state live-engine capability
- **THEN** the capability SHALL remain additive under the existing Codex CLI leader model
- **AND** it SHALL not present the recovery-aware provenance-state live engine as a separate replacement runtime outside the current user-level orchestration line
