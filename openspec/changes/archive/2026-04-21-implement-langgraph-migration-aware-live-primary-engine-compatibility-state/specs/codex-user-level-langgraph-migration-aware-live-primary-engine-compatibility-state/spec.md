## ADDED Requirements

### Requirement: The user-level LangGraph lane SHALL expose migration-aware live primary-engine compatibility-state semantics as an additive durable capability

The user-level LangGraph durable lane SHALL expose migration-aware live primary-engine compatibility-state semantics as an additive durable capability under the existing Codex CLI leader model.

#### Scenario: Operator inspects the user-level migration-aware live-engine capability

- **WHEN** the operator inspects the user-level LangGraph migration-aware live-engine capability
- **THEN** the capability SHALL remain additive under the existing Codex CLI leader model
- **AND** it SHALL not present the migration-aware live engine as a separate replacement runtime outside the current user-level orchestration line
