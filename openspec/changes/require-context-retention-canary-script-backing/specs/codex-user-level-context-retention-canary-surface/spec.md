## MODIFIED Requirements

### Requirement: Canary placement SHALL have executable enforcement

The repository SHALL provide an executable checker that validates active canary placement and recovery wording without relying on model memory alone.

The checker SHALL fail closed when:

- either startup summary is missing the literal canary prompt
- either startup summary omits `AGENTS.md` from its canary recovery action
- `AGENTS.md` contains the literal canary prompt
- an active non-startup-summary file duplicates the literal canary prompt text

The checker MAY ignore immutable historical archives, external worktrees, caches, runtime state, and binary files.

#### Scenario: Startup recovery omits repository instructions

- **WHEN** either startup summary describes canary recovery
- **AND** the recovery action does not mention `AGENTS.md`
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report the startup summary path

#### Scenario: Repository instructions duplicate the literal prompt

- **WHEN** `AGENTS.md` contains the literal canary prompt text
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report that `AGENTS.md` must remain a recovery reread target rather than a literal prompt source
