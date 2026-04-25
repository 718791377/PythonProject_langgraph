## ADDED Requirements

### Requirement: Generated controls SHALL persist the durable orchestration backend selection
The generated user-level control surface SHALL persist the durable orchestration backend as a separate explicit selector.

At minimum the selector SHALL support:

- `native_omx`
- `langgraph`

The default durable orchestration backend SHALL remain the current native path until LangGraph is explicitly selected.

#### Scenario: Fresh install preserves the current backend by default
- **WHEN** the installer creates a fresh user-level control state
- **THEN** the durable orchestration backend selector SHALL default to `native_omx`
- **AND** LangGraph SHALL remain additive rather than replacing the current durable path automatically
