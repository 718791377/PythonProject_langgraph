## MODIFIED Requirements
### Requirement: Canary placement SHALL have executable enforcement

The repository SHALL provide an executable checker that validates active canary placement, canary encoding integrity, recovery wording, and optional user-provided response/session evidence without relying on model memory alone.

The checker SHALL continue to enforce static placement rules for repository files.

When response or session evidence is explicitly provided, the checker SHALL inspect only user-visible assistant responses and SHALL NOT count tool output, compaction summaries, reasoning, developer/system payloads, startup-summary file reads, or other context copies as satisfying the canary.

When session JSONL evidence is narrowed to a specific turn or latest assistant response, the checker SHALL apply that selection only to eligible assistant messages and SHALL continue to ignore non-user-visible context sources.

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

### Requirement: Startup instruction surfaces SHALL have mojibake enforcement

The repository SHALL provide an executable checker that scans active startup and instruction authority surfaces through explicit UTF-8 reads and fails when those surfaces contain mojibake or lossy replacement text. The checker SHALL also support explicit response/session evidence diagnostics for startup canary mojibake without writing the literal canary into any additional authority surface.

#### Scenario: Response evidence contains mojibake startup canary

- **WHEN** the checker receives response text or a session JSONL containing an eligible assistant response
- **AND** that response includes a legacy-encoding mojibake rendering of the startup canary
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report `mojibake_canary`
- **AND** it SHALL recommend rereading the startup summary pair through an explicit UTF-8 path
