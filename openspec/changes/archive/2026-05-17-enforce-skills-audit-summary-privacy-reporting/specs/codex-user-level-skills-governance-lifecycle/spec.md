## ADDED Requirements

### Requirement: Skills usage audit Markdown summaries SHALL expose evidence privacy gates

The skills usage audit sanitized Markdown summaries SHALL expose the same evidence-retention privacy gates that are used by the JSON report field contract and profile-candidate gate.

The audit Markdown summary MUST show explicit-skill noise-token privacy state and manual-note source-path privacy state. The profile-candidate Markdown summary MUST show source-report privacy status and any source-report privacy violations or blockers. These summaries MUST remain sanitized and MUST NOT include raw transcripts, raw local paths, tokens, cookies, or user-level configuration contents.

#### Scenario: Reviewer reads a sanitized audit summary

- **WHEN** the audit script renders `--summary-output`
- **THEN** the Markdown SHALL show whether raw explicit-skill noise tokens were retained
- **AND** it SHALL show the noise-token privacy policy and maximum retained token length
- **AND** it SHALL show whether manual-note source paths were retained
- **AND** it SHALL show the manual-note source-path privacy policy and maximum retained source-path length

#### Scenario: Reviewer reads a profile-candidate summary

- **WHEN** the audit script renders `--candidate-summary-output`
- **THEN** the Markdown SHALL show source-report privacy status
- **AND** it SHALL show source-report privacy violations or `none`
- **AND** it SHALL remain non-mutating and preview-only unless a later separate explicit apply authorization is given
