## ADDED Requirements

### Requirement: Legacy Resumed Sessions SHALL Remain Compatibility-Scoped

The repository workflow SHALL treat legacy resumed Codex sessions as compatibility-scoped sessions.

A legacy resumed session is an older Codex `/resume` thread that may retain stale context, stale MCP assumptions, or stale launcher behavior from before the current governance state.

Legacy resumed sessions MAY continue temporarily, but they SHALL NOT override current repository files, current local Git state, active OpenSpec state, or session-ownership claims.

#### Scenario: Old resumed session disagrees with current repository state

- **GIVEN** a legacy resumed session contains stale instructions or stale MCP assumptions
- **WHEN** the session is used for follow-up discussion
- **THEN** the current repository files and current local Git state SHALL be treated as authoritative
- **AND** the old session SHALL NOT claim new governance implementation without revalidating startup summaries, OpenSpec state, Git state, and session-ownership claims

#### Scenario: Old resumed session needs a scoped workaround

- **GIVEN** a legacy resumed session cannot start because of stale runtime or MCP state
- **WHEN** the operator wants to continue that old thread
- **THEN** the session MAY use a per-invocation compatibility override
- **AND** that override SHALL NOT become a permanent global configuration change unless a future approved governance change says so
