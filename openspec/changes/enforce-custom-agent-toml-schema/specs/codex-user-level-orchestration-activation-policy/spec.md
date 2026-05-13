## MODIFIED Requirements

### Requirement: Agent, skill, profile, and follow-up surfaces SHALL stay distinct
The orchestration activation policy SHALL keep native Codex subagents, workflow skills, plugin-provided skills, profile helpers, durable workers, and LangGraph nodes as distinct execution surfaces. Skills SHALL load from `SKILL.md` files and skills are not native subagents. Profile hard-load or soft-load SHALL NOT by itself start durable workers or satisfy persistent-team thresholds. Follow-up work after a completed and absorbed expert SHALL spawn a fresh agent unless the user explicitly asks to preserve the thread or a plan records a preserved-thread reason.

Standalone native-agent TOMLs SHALL remain separately checker-backed: present user-level and repo-local agent TOMLs SHALL pass `tools/check_custom_agent_toml_schema.py` by defining non-empty top-level `name`, `description`, and `developer_instructions` fields.

#### Scenario: A skill is invoked during an activation flow
- **WHEN** a workflow skill or plugin profile is used
- **THEN** the final evidence label SHALL NOT treat that invocation as a returned native expert result
- **AND** any later expert follow-up SHALL use a fresh agent unless preservation is explicit

#### Scenario: Native-agent TOML schema is checked
- **WHEN** the activation policy guard runs custom agent TOML schema validation
- **THEN** native-agent TOML validity SHALL be evaluated separately from skill `SKILL.md` validity
- **AND** missing or empty `name`, `description`, or `developer_instructions` fields SHALL fail the checker for any present standalone agent TOML
