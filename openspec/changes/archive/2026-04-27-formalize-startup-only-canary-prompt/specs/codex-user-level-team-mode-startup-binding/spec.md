# codex-user-level-team-mode-startup-binding Specification Delta

## ADDED Requirements

### Requirement: Startup-binding surfaces SHALL avoid duplicating project canary prompts

Startup-binding, launcher, and repository instruction surfaces SHALL NOT duplicate a project-level context-retention canary prompt outside the project startup summary pair.

They MAY point to the project startup summary as the source of truth and MAY describe the cold-start recovery path.

#### Scenario: Launcher or instruction text refers to context-loss recovery

- **WHEN** startup-binding or repository instruction text documents context-loss recovery
- **THEN** it SHALL refer readers to the project startup summary for the canary prompt
- **AND** it SHALL NOT embed the literal canary prompt text in launcher payloads, generated wrappers, or `AGENTS.md`
