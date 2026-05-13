## MODIFIED Requirements

### Requirement: Capability switch chains SHALL be executable-policy checked
The orchestration activation policy SHALL treat capability switches as a strict dependency chain and SHALL use `tools/check_capability_switch_chain.py` as executable policy support for present user-level state. `subagent_routing=off` SHALL require higher orchestration layers to be off, `oh_my_codex=off` SHALL require `langgraph=off`, and `durable_orchestration_backend=langgraph` SHALL require `langgraph=on`.

#### Scenario: Activation policy guard checks switch dependencies
- **WHEN** the orchestration activation policy guard runs
- **THEN** it SHALL invoke or embed the capability-switch dependency checker
- **AND** invalid present state combinations SHALL fail as capability-chain violations
