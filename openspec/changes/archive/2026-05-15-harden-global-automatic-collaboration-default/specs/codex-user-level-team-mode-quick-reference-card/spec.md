## ADDED Requirements

### Requirement: The quick-reference card SHALL preserve the automatic collaboration default

The generated user-level quick-reference card SHALL include a concise global automatic collaboration default section. The section SHALL state that automatic collaboration is on by default for all projects and all user-level Codex sessions, that the user does not need to repeat collaboration reminder phrases, and that native `spawn_agent` platform/tool constraints must be reported as concrete blockers rather than missing-reminder reasons.

#### Scenario: Operator opens regenerated quick-reference card

- **WHEN** the user-level installer regenerates `docs/team-mode-quick-reference.md`
- **THEN** the card SHALL contain a global automatic collaboration default section
- **AND** it SHALL mention automatic evaluation of native experts, `native_omx`, LangGraph durable workflow, and persistent team for qualifying tasks
- **AND** it SHALL include `experts=blocked:platform_subagent_invocation_constraint` for native subagent platform/tool blockers
- **AND** it SHALL preserve threshold-gated durable/persistent team selection language
