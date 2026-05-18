## ADDED Requirements

### Requirement: Automatic collaboration SHALL be the user-level default

The user-level orchestration activation policy SHALL define automatic collaboration as the default for all projects and all Codex sessions launched through the user-level workflow. The operator SHALL NOT need to repeat phrases such as "use experts", "use durable_team", "use persistent team", "parallel", or "subagents" for routing to evaluate experts, durable workflow, and persistent team.

When a task qualifies by scope, risk, multi-document work, multi-stage workflow, independent execution slices, or stabilization need, the session SHALL automatically evaluate and adopt the smallest sufficient collaboration surface among native experts, `native_omx`, LangGraph durable workflow, and persistent team.

#### Scenario: Large task starts without repeated prompt reminder

- **WHEN** a new or resumed session receives a qualifying multi-stage or multi-document task
- **THEN** the activation trace SHALL evaluate experts, durable workflow, and persistent team without requiring the operator to repeat a collaboration reminder
- **AND** the trace SHALL cite phase, thresholds, readiness, blockers, or main-session takeover rather than missing user reminders

#### Scenario: Native subagent invocation is platform-blocked

- **WHEN** native expert routing is appropriate but the current platform/tool contract blocks direct `spawn_agent` invocation
- **THEN** the activation trace SHALL report `experts=blocked:platform_subagent_invocation_constraint`
- **AND** the session SHALL continue through an eligible durable lane, a narrower available expert path, or explicit main-session takeover
- **AND** the blocker SHALL NOT be rewritten as "the user did not request subagents" or equivalent missing-reminder language

### Requirement: Generated startup instructions SHALL preserve the automatic collaboration default

Generated user-level startup model instructions and the generated `team-leader.toml` profile SHALL include the global automatic collaboration default and the concrete platform-subagent blocker rule.

#### Scenario: Wrapped launcher emits model instructions

- **WHEN** a wrapped Codex launcher creates the file-backed model instructions payload
- **THEN** the payload SHALL state that automatic collaboration is the default
- **AND** it SHALL state that the user does not need to repeat experts, durable_team, or persistent team reminders
- **AND** it SHALL preserve `platform_subagent_invocation_constraint` as the platform/tool blocker token

#### Scenario: Team leader profile is generated

- **WHEN** the user-level installer generates `team-leader.toml`
- **THEN** the profile SHALL include the global automatic collaboration default
- **AND** it SHALL forbid using missing user reminders as the reason to skip orchestration
