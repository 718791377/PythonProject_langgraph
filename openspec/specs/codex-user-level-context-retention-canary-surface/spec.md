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

The repository SHALL provide an executable checker that validates active canary placement, canary encoding integrity, recovery wording, and optional user-provided response/session evidence without relying on model memory alone.

The checker SHALL continue to enforce static placement rules for repository files.

When response or session evidence is explicitly provided, the checker SHALL inspect only user-visible assistant responses and SHALL NOT count tool output, compaction summaries, reasoning, developer/system payloads, startup-summary file reads, or other context copies as satisfying the canary.

When session JSONL evidence is narrowed to a specific turn or latest assistant response, the checker SHALL apply that selection only to eligible assistant messages and SHALL continue to ignore non-user-visible context sources.

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

#### Scenario: User-visible assistant response is missing the canary

- **WHEN** the checker receives response text or a session JSONL containing an eligible assistant response
- **AND** that assistant response does not include the startup-summary-defined canary markers
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report `missing_canary`
- **AND** it SHALL recommend cold-start rereading the startup summary pair and required read order

#### Scenario: Tool output contains canary text but assistant response omits it

- **WHEN** a session JSONL contains tool output or file-read output with canary markers
- **AND** the eligible assistant response omits the markers
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report `missing_canary`
- **AND** it SHALL NOT treat the tool output as satisfying the response diagnostic

#### Scenario: Selected turn assistant response is the canonical evidence source

- **WHEN** the checker receives session JSONL evidence together with a selected turn id or latest-assistant selector
- **AND** the selected assistant response contains the startup-summary-defined canary markers
- **THEN** the checker SHALL report `canonical_present`
- **AND** it SHALL ignore other turns' context copies and assistant messages outside the selected turn scope

#### Scenario: Assistant response contains mojibake canary text

- **WHEN** the eligible assistant response contains a legacy-encoding mojibake rendering of either canary marker
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report `mojibake_canary`
- **AND** it SHALL state that the UTF-8 startup summary pair is canonical

### Requirement: OpenSpec guard SHALL run the canary placement checker

The repository OpenSpec guard SHALL run the canary placement checker as part of its standard verification sequence.

#### Scenario: OpenSpec guard runs on a cold-start clone

- **WHEN** `python tools/run_openspec_guard.py --root . --json` runs in a repository clone
- **THEN** the aggregated guard output SHALL include a `check_context_retention_canary_surface` step
- **AND** the guard SHALL fail if the checker reports canary placement errors

### Requirement: Startup instruction surfaces SHALL have mojibake enforcement

The repository SHALL provide an executable checker that scans active startup and instruction authority surfaces through explicit UTF-8 reads and fails when those surfaces contain mojibake or lossy replacement text. The checker SHALL also support explicit response/session evidence diagnostics for startup canary mojibake without writing the literal canary into any additional authority surface.

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

#### Scenario: Response evidence contains mojibake startup canary

- **WHEN** the checker receives response text or a session JSONL containing an eligible assistant response
- **AND** that response includes a legacy-encoding mojibake rendering of the startup canary
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report `mojibake_canary`
- **AND** it SHALL recommend rereading the startup summary pair through an explicit UTF-8 path

### Requirement: OpenSpec guard SHALL run the startup instruction mojibake checker

The repository OpenSpec guard SHALL run the startup instruction mojibake checker as part of its standard verification sequence after the canary-surface checker.

#### Scenario: OpenSpec guard checks instruction encoding integrity

- **WHEN** `python tools/run_openspec_guard.py --root . --json` runs in a repository clone
- **THEN** the aggregated guard output SHALL include a `check_startup_instruction_mojibake` step
- **AND** the guard SHALL fail if the checker reports mojibake or lossy replacement text
