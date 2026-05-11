# Codex User-Level Capability Switches

## Purpose

Define layered user-level capability switches for native routing, oh-my-codex durable features, and LangGraph availability.

This capability separates enabled orchestration layers from per-task effective-lane choice.
## Requirements
### Requirement: The user-level installation SHALL expose layered capability switches

The user-level installation SHALL expose layered capability switches for:

- native expert routing availability
- oh-my-codex durable-feature availability
- LangGraph availability

These switches SHALL be operator-visible and SHALL not collapse back into one opaque durable-backend-only control model.

#### Scenario: Operator inspects the layered capability state

- **WHEN** the operator inspects the user-level control state
- **THEN** the state SHALL distinguish the enabled capability layers
- **AND** it SHALL not force the operator to infer enabled capabilities only from one backend selector value

### Requirement: The layered switch model SHALL preserve dependency rules

The layered switch model SHALL preserve explicit dependency constraints among the capability layers.

At minimum:

- turning routing off SHALL disable higher orchestration layers
- turning LangGraph on SHALL require the oh-my-codex durable layer to remain enabled

#### Scenario: Invalid layered state is rejected or normalized

- **WHEN** the operator or runtime attempts to enable `langgraph` while the prerequisite durable layer is disabled
- **THEN** the user-level model SHALL reject or normalize that state
- **AND** it SHALL keep the resulting state explicit and inspectable

### Requirement: Capability switches SHALL be read as a dependency chain

The user-level capability switch policy SHALL require orchestration state to be read in dependency-chain order: `subagent_routing` first, then `oh_my_codex`, then `langgraph`.

LangGraph SHALL be considered available only when routing is not off and oh-my-codex is on.

#### Scenario: LangGraph is ready

- **WHEN** `subagent_routing` is not off, `oh_my_codex=on`, `langgraph=on`, and `langgraph_ready=true`
- **THEN** activation output SHALL report LangGraph as the default ready durable backend
- **AND** it SHALL NOT infer that a persistent team is already running only from backend readiness
