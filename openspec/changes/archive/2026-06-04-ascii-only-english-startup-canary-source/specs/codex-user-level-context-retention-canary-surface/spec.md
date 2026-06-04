## MODIFIED Requirements

### Requirement: Canary prompt text SHALL live only in the startup summary pair

The repository SHALL maintain context-retention canary authority only in the active bilingual startup summary pair:

- `docs_bilingual/project_startup_summary.md` - English startup summary and ASCII-only recovery/source description.
- `docs_bilingual/project_startup_summary.zh-CN.md` - Chinese startup summary and literal visible marker source.

The English startup summary SHALL NOT contain non-ASCII characters, literal visible canary marker text, legacy ASCII marker tokens, or mojibake variants of the visible markers. It SHALL describe the current visible markers through ASCII-only Unicode codepoint notation or equivalent ASCII-only indirection.

The Chinese startup summary SHALL contain the literal visible marker text and SHALL remain UTF-8-clean.

Other active instruction surfaces MAY refer to the startup-summary canary and MAY describe the cold-start recovery action, but SHALL NOT duplicate the literal canary prompt text.

#### Scenario: English startup summary uses ASCII-only marker indirection

- **WHEN** the canary placement checker scans `docs_bilingual/project_startup_summary.md`
- **THEN** it SHALL require the file to be ASCII-only
- **AND** it SHALL fail if that file contains the literal visible canary markers or their mojibake variants

#### Scenario: Chinese startup summary remains the literal marker source

- **WHEN** the canary placement checker scans `docs_bilingual/project_startup_summary.zh-CN.md`
- **THEN** it SHALL require both literal visible marker values to be present
- **AND** it SHALL fail if the file contains mojibake marker text

### Requirement: Canary placement SHALL have executable enforcement

The repository SHALL provide an executable checker that validates active canary placement, canary encoding integrity, recovery wording, and optional user-provided response/session evidence without relying on model memory alone.

The visible startup canary markers SHALL remain the startup-summary-defined non-ASCII/cat-sound marker pair. The literal marker text SHALL be stored in the Chinese startup summary, while the English startup summary SHALL use ASCII-only codepoint indirection. Previous ASCII transport-stable markers SHALL NOT be accepted as current canonical response evidence; they MAY remain only as checker-internal legacy/stale compatibility inputs and replay-filtering signals.

The checker SHALL continue to enforce static placement rules for repository files.

When response or session evidence is explicitly provided, the checker SHALL inspect only user-visible assistant responses and SHALL NOT count tool output, compaction summaries, reasoning, developer/system payloads, startup-summary file reads, or other context copies as satisfying the canary.

#### Scenario: User-visible assistant response uses the canonical visible marker pair

- **WHEN** the checker receives response text or session JSONL with an eligible assistant response
- **AND** that response contains both startup-summary-defined visible markers
- **THEN** the checker SHALL report `canonical_present`
