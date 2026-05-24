# codex-user-level-context-retention-canary-surface Specification

## Purpose
Define where the context-retention canary prompt is allowed to live and require executable checks that detect prompt-placement drift before cold-start sessions rely on stale or duplicated instructions.
## Requirements
### Requirement: Canary prompt text SHALL live only in the startup summary pair

The repository SHALL maintain the literal context-retention canary prompt only in the active bilingual startup summary pair:

- `docs_bilingual/project_startup_summary.md` - English startup summary and canary prompt source.
- `docs_bilingual/project_startup_summary.zh-CN.md` - Chinese startup summary and canary prompt source.

Other active instruction surfaces MAY refer to the startup-summary canary and MAY describe the cold-start recovery action, but SHALL NOT duplicate the literal canary prompt text.

#### Scenario: Repository instructions refer to the canary without duplicating it

- **WHEN** `AGENTS.md` documents context-loss recovery
- **THEN** it SHALL point to the startup summary as the canary source of truth
- **AND** it SHALL NOT contain the literal canary prompt text

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

### Requirement: OpenSpec guard SHALL run the canary placement checker

The repository OpenSpec guard SHALL run the canary placement checker as part of its standard verification sequence.

#### Scenario: OpenSpec guard runs on a cold-start clone

- **WHEN** `python tools/run_openspec_guard.py --root . --json` runs in a repository clone
- **THEN** the aggregated guard output SHALL include a `check_context_retention_canary_surface` step
- **AND** the guard SHALL fail if the checker reports canary placement errors

### Requirement: Startup instruction surfaces SHALL have mojibake enforcement

The repository SHALL provide an executable checker that scans active startup and instruction authority surfaces through explicit UTF-8 reads and fails when those surfaces contain mojibake or lossy replacement text.

The checker SHALL fail closed when any configured startup or instruction authority surface:

- cannot be read as UTF-8
- contains a Unicode replacement character
- contains a run of three or more question marks that indicates lossy replacement
- contains a generated legacy-encoding mojibake variant of a configured startup, canary, or orchestration token

The checker MAY limit its scope to active startup and governance authority surfaces and MAY exclude historical memory notes, archived OpenSpec changes, generated reports, caches, runtime state, and broad documentation trees.

#### Scenario: Repository instructions contain startup mojibake

- **WHEN** `AGENTS.md` contains a legacy-encoding mojibake rendering of a configured startup token
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report `AGENTS.md` in its findings

#### Scenario: Governance authority contains lossy question replacements

- **WHEN** an active startup/governance authority surface contains a run of three or more question marks caused by lossy replacement
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report the path and line number

#### Scenario: Startup summary contains replacement characters

- **WHEN** either startup summary contains a Unicode replacement character
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report the startup summary path

### Requirement: OpenSpec guard SHALL run the startup instruction mojibake checker

The repository OpenSpec guard SHALL run the startup instruction mojibake checker as part of its standard verification sequence after the canary-surface checker.

#### Scenario: OpenSpec guard checks instruction encoding integrity

- **WHEN** `python tools/run_openspec_guard.py --root . --json` runs in a repository clone
- **THEN** the aggregated guard output SHALL include a `check_startup_instruction_mojibake` step
- **AND** the guard SHALL fail if the checker reports mojibake or lossy replacement text
