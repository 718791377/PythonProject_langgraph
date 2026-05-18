## ADDED Requirements

### Requirement: Skills usage audit Markdown summaries SHALL expose advisory decision buckets

The skills usage audit sanitized Markdown summary SHALL expose advisory decision buckets derived from module evidence so reviewers can distinguish default/project profile review candidates from on-demand, manual-review, and dormant modules without opening raw JSON.

Decision buckets MUST remain non-mutating review inputs. They MUST NOT mark profile apply as allowed and MUST NOT replace a later profile apply candidate record or explicit apply authorization.

#### Scenario: Reviewer reads advisory decision buckets

- **WHEN** the audit script generates JSON and Markdown summary output
- **THEN** the report SHALL include advisory decision buckets for profile-review candidates, on-demand soft-load modules, manual-review medium/weak modules, and dormant/restorable modules
- **AND** the Markdown summary SHALL render those buckets in the decision recommendation section
- **AND** the summary SHALL state that profile apply is not allowed by the summary itself
