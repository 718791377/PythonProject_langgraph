## MODIFIED Requirements

### Requirement: Capability switch chains SHALL be executable-policy checked
The user-level capability switch policy SHALL be backed by an executable checker for dependency-chain consistency. The checker SHALL validate that `subagent_routing=off` disables higher orchestration layers, `oh_my_codex=off` disables LangGraph, `langgraph=on` requires routing to be available and oh-my-codex to be on, and `durable_orchestration_backend=langgraph` requires `langgraph=on`.

The repository SHALL provide `tools/check_capability_switch_chain.py` to validate the user-level capability state JSON and optional repo-local `.omx/state/langgraph/backend.json` context. The checker SHALL allow missing user-level state in clean CI when not required, but SHALL fail invalid present state combinations.

#### Scenario: Capability chain checker rejects an invalid state

- **WHEN** the capability state contains `subagent_routing=off` while `oh_my_codex=on` or `langgraph=on`
- **THEN** the checker SHALL fail with a capability-chain violation
- **AND** it SHALL identify the invalid dependency instead of silently normalizing it in the report

#### Scenario: LangGraph backend selection is checked

- **WHEN** the capability state contains `durable_orchestration_backend=langgraph`
- **THEN** the checker SHALL require `langgraph=on`, `oh_my_codex=on`, and `subagent_routing!=off`
- **AND** if `langgraph_ready=true` is present it SHALL require LangGraph to be the selected durable backend
