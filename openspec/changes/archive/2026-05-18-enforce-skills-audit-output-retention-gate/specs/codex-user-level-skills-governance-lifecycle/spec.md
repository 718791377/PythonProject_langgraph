## MODIFIED Requirements

### Requirement: Skills usage audit output retention gates SHALL block local-only raw audit artifacts

The skills usage audit lifecycle SHALL keep raw audit outputs local-only unless they have been converted into an explicitly reviewed sanitized long-term evidence document.

The repository guard MUST run a Skills audit output-retention check that fails when any `.tmp/` artifact is tracked, staged, changed, or commit-visible untracked. The same check MUST fail when raw Skills usage audit JSON reports with names beginning `skills-usage-audit`, `skills-usage-baseline`, `skills-usage-warning`, or `skills-usage-report` are retained outside `.tmp/`.

Sanitized Markdown summaries MAY be retained as long-term evidence after privacy review. Raw session transcripts, raw JSON audit reports, private paths, tokens, and vendor-cache contents MUST NOT be retained as durable Git evidence for this audit.

#### Scenario: Forced `.tmp` raw audit report is staged

- **WHEN** `.tmp/skills-usage-audit-30d.json` is forced into Git or otherwise becomes tracked, staged, changed, or commit-visible untracked
- **THEN** the output-retention check SHALL fail
- **AND** it SHALL report both the `.tmp/` artifact retention violation and the raw audit JSON retention violation when both apply

#### Scenario: Raw audit JSON is retained outside `.tmp`

- **WHEN** `reports/skills-usage-baseline-2026-05-18.json` or another raw `skills-usage-*.json` audit report is tracked, staged, changed, or commit-visible untracked outside `.tmp/`
- **THEN** the output-retention check SHALL fail
- **AND** the reviewer SHALL regenerate or retain only a sanitized Markdown summary for long-term evidence

#### Scenario: Sanitized Markdown evidence is retained

- **WHEN** a reviewed `skills-usage-audit-30d-summary.md` or equivalent sanitized Markdown summary is retained
- **THEN** the output-retention check SHALL pass for that summary
- **AND** the summary SHALL remain subject to the audit privacy and data-minimization requirements
