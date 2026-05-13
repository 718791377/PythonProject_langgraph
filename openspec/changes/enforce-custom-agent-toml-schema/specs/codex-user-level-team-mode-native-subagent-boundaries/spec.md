## MODIFIED Requirements

### Requirement: Custom native-subagent TOMLs SHALL use layered locations and a minimum standalone schema
The workflow SHALL preserve two layered custom-agent locations:

- user-level reusable roles under the Codex home agent directory
- repository-specific roles under `<repo>/.codex/agents/`

Every standalone custom-agent TOML used by this workflow SHALL define at least:

- `name` - required native-agent TOML field for the agent role name.
- `description` - required native-agent TOML field for the role summary.
- `developer_instructions` - required native-agent TOML field for role-specific behavior instructions.

The repository SHALL provide an executable custom agent TOML schema checker that validates present user-level and repo-local standalone agent TOMLs for parseability and non-empty top-level `name`, `description`, and `developer_instructions` string fields. Missing agent directories SHALL be reported as warnings, not failures.

#### Scenario: Maintainer checks role placement rules
- **WHEN** a maintainer reads the generated guidance for reusable and repository-scoped roles
- **THEN** it SHALL distinguish user-level reusable agent TOMLs from repository-scoped agent TOMLs
- **AND** it SHALL state the minimum standalone custom-agent fields

#### Scenario: Custom agent TOML schema checker runs
- **WHEN** `python tools/check_custom_agent_toml_schema.py --root . --json` runs
- **THEN** every present standalone custom-agent TOML under the configured user-level and repo-local agent directories SHALL parse as TOML
- **AND** each checked TOML SHALL contain non-empty top-level `name`, `description`, and `developer_instructions` string fields
- **AND** a missing agent directory SHALL produce a warning rather than failing the check
