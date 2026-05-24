## MODIFIED Requirements

### Requirement: Canary placement SHALL have executable enforcement

The repository SHALL provide an executable checker that validates active canary placement, canary encoding integrity, and recovery wording without relying on model memory alone.

The checker SHALL fail closed when:

- either startup summary is missing the literal canary prompt
- either startup summary omits `AGENTS.md` from its canary recovery action
- either startup summary contains a mojibake or replacement-character variant of the canary prompt
- `AGENTS.md` contains the literal canary prompt
- `AGENTS.md` contains a mojibake or replacement-character variant of the canary prompt
- an active non-startup-summary file duplicates the literal canary prompt text
- an active non-archived text file contains a mojibake or replacement-character variant of the canary prompt

The checker MAY ignore immutable historical archives, external worktrees, caches, runtime state, generated gate reports, gitignored local logs, and binary files.

#### Scenario: Startup recovery omits repository instructions

- **WHEN** either startup summary describes canary recovery
- **AND** the recovery action does not mention `AGENTS.md`
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report the startup summary path

#### Scenario: Repository instructions duplicate the literal prompt

- **WHEN** `AGENTS.md` contains the literal canary prompt text
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report that `AGENTS.md` must remain a recovery reread target rather than a literal prompt source

#### Scenario: Repository instructions contain mojibake canary text

- **WHEN** `AGENTS.md` contains a corrupted legacy-encoding rendering of either canary marker
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report the path and line containing the corrupted marker

#### Scenario: Startup summary contains mojibake canary text

- **WHEN** either startup summary contains a corrupted legacy-encoding rendering of either canary marker
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report that the startup summary canary source is not UTF-8-clean
