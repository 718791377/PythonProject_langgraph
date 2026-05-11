## ADDED Requirements

### Requirement: Capability switches SHALL be read as a dependency chain

The user-level capability switch policy SHALL require orchestration state to be read in dependency-chain order: `subagent_routing` first, then `oh_my_codex`, then `langgraph`.

LangGraph SHALL be considered available only when routing is not off and oh-my-codex is on.

#### Scenario: LangGraph is ready

- **WHEN** `subagent_routing` is not off, `oh_my_codex=on`, `langgraph=on`, and `langgraph_ready=true`
- **THEN** activation output SHALL report LangGraph as the default ready durable backend
- **AND** it SHALL NOT infer that a persistent team is already running only from backend readiness
