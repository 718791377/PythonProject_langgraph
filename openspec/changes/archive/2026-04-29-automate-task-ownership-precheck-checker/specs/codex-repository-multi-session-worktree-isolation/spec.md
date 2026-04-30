## ADDED Requirements

### Requirement: Session ownership checker SHALL support task ownership precheck

The repository SHALL provide an optional task ownership precheck mode in `tools/check_session_ownership_claims.py`.

The precheck mode SHALL inspect deterministic semantic ownership signals across registered Git worktrees, local branches, remote-tracking branches, active OpenSpec changes, active session claim files, target paths, and ignored/local-only guard-scanned files.

#### Scenario: Matching clean branch claims a task before edits begin

- **WHEN** the checker runs in task ownership precheck mode with a term matching an existing clean feature branch
- **THEN** it SHALL classify the task as `claimed-not-started`
- **AND** it SHALL return a non-zero exit code so a new writer does not create a duplicate work scope silently

#### Scenario: Matching active claim indicates in-progress ownership

- **WHEN** the checker runs in task ownership precheck mode with a target matching an active claim file
- **THEN** it SHALL classify the task as `in-progress`
- **AND** it SHALL report the matching claim file and path or OpenSpec change signal

#### Scenario: Matching ignored guard target is reported

- **WHEN** the checker runs in task ownership precheck mode with a target path or term matching an ignored/local-only file under a guard-scanned directory
- **THEN** it SHALL report that ignored file as an ownership signal
- **AND** it SHALL not delete, move, or modify the file

### Requirement: Task ownership precheck SHALL keep GitLab MR inspection explicit

The task ownership precheck SHALL offer an explicit GitLab MR inspection option without making repository guard execution depend on network access.

#### Scenario: GitLab MR inspection is unavailable but required

- **WHEN** the checker runs in task ownership precheck mode with GitLab MR inspection required
- **AND** the checker cannot inspect open GitLab MRs because token or remote metadata is unavailable
- **THEN** it SHALL fail with an operator-facing error
- **AND** it SHALL leave the repository unchanged
