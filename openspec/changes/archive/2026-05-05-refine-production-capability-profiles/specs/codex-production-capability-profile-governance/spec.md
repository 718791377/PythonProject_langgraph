# codex-production-capability-profile-governance Specification Delta

## ADDED Requirements

### Requirement: Production Plan Separates Durable-Team Dependencies From Business Runtime Dependencies

The production durable-team plan SHALL state that third-party dependencies for evaluation, GUI control, queues, embeddings, vector retrieval, and recovery tooling belong to the Codex CLI durable-team runtime by default and SHALL NOT be reused as concrete business runtime dependencies unless a separate business project explicitly declares and owns them.

#### Scenario: PySide6 appears in the production durable-team plan

- **GIVEN** the plan lists `PySide6` as a local GUI control-center dependency
- **WHEN** a concrete business project also needs a desktop GUI
- **THEN** the plan treats the Codex CLI durable-team GUI and the concrete business GUI as separate systems
- **AND** the business project must own its own GUI dependency, packaging, state, and release rules

### Requirement: Local Llama Model Service Is The Only Shared Dependency Exception

The production durable-team plan SHALL allow local Llama model deployments to act as shared model services only through provider adapters that separate policy, logging, permissions, prompts, secrets, and data boundaries.

#### Scenario: A business workload and the durable team both use a local model

- **GIVEN** both surfaces call the same local model service
- **WHEN** the calls are routed through provider profiles
- **THEN** the durable team state, business state, secrets, prompts, and logs remain separated

### Requirement: Business Capability Profiles Stay Abstract In The Main Plan

The production durable-team plan SHALL describe abstract capability profiles instead of naming concrete businesses in the main plan.

#### Scenario: A new concrete workload is evaluated

- **GIVEN** a maintainer receives a new workload example
- **WHEN** the maintainer plans support for that workload
- **THEN** the workload maps to one or more abstract capability profiles
- **AND** concrete names are recorded only in the separate reference table
