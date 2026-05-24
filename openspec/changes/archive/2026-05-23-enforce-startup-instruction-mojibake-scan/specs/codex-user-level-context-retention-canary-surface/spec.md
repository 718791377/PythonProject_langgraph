## ADDED Requirements

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
