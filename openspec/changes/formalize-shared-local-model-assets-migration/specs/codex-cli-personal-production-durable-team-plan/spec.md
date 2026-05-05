# codex-cli-personal-production-durable-team-plan Specification Delta

## ADDED Requirements

### Requirement: Shared Local Model Assets Migration Is Documented Separately

The production durable-team documentation SHALL include a separate migration plan for local llama and GGUF model assets that explains how `D:\PythonProject_langgraph` can centrally manage ignored model assets while consumer repositories call them through explicit provider profiles.

#### Scenario: A maintainer migrates local GGUF files

- **GIVEN** a maintainer wants to move GGUF model files into the orchestration repository tree
- **WHEN** they read the migration plan
- **THEN** the plan identifies ignored model asset directories, Git hygiene checks, provider profiles, validation commands, and rollback guidance
- **AND** it states that actual GGUF model files are not committed to ordinary Git

### Requirement: Local Model Providers Are Services And Not Durable Truth

The production durable-team documentation SHALL state that local model providers such as `local-judge-qwen` and `local-embed-jina` are shared services only and SHALL NOT become durable truth, approval authority, or backend routing selectors.

#### Scenario: OpenClaw starts a shared local model service

- **GIVEN** OpenClaw starts or calls a model service managed under `D:\PythonProject_langgraph`
- **WHEN** the service handles requests
- **THEN** OpenClaw state, Codex durable-team state, approval state, customer data, and provider logs remain separated

### Requirement: Production Durable-Team Implementation Has A Playbook Layer

The production durable-team plan SHALL point to a playbook that converts the draft target into release slices with preconditions, file scopes, forbidden scopes, commands, evidence, validation, and rollback guidance.

#### Scenario: A cold-start maintainer resumes implementation

- **GIVEN** the maintainer has no prior conversation context
- **WHEN** they open the playbook
- **THEN** they can identify the next release slice, its OpenSpec requirement, its allowed file scope, its validation commands, and whether runtime apply mode is allowed

### Requirement: Expert Fan-Out And Stalled Subagent Handling Are Explicit

The team-mode plan SHALL state that bounded multi-face research starts with homogeneous analyst fan-out and that unfinished subagents must be diagnosed before being skipped or closed.

#### Scenario: One specialist subagent has not completed

- **GIVEN** analyst fan-in is complete but a specialist subagent is still running
- **WHEN** the leader prepares a final answer
- **THEN** the leader first records whether the subagent is still active, blocked, or suspected stalled
- **AND** the leader decides whether to wait, narrow and respawn, close with recorded cause, or continue locally with that limitation disclosed
