## ADDED Requirements

### Requirement: Skills usage audit field contracts SHALL validate module evidence rows

The skills usage audit report field contract SHALL validate every `module_evidence` row before that evidence can drive advisory decision buckets or profile-candidate generation.

Each module evidence row MUST include the module name, plugin list, strong helper-call count, strong skill-path-read count, strong total, default-candidate threshold, mapped-tool-call medium-evidence count and policy, medium-evidence rationale, weak plugin mentions, cross-project utility, and advisory recommendation. Numeric counts MUST be non-negative integers, `strong_total` MUST equal strong helper calls plus strong skill-path reads, plugin entries MUST be strings, mapped tool-call evidence MUST remain medium evidence only, cross-project utility MUST require manual review, and recommendations MUST remain within the approved advisory recommendation set.

#### Scenario: Candidate gate receives a report with invalid module evidence

- **WHEN** profile-candidate generation validates an audit report
- **AND** any `module_evidence` row is missing required fields, has wrong-typed values, contains non-string plugin entries, has negative counts, has a stale `strong_total`, treats mapped tool calls as strong evidence, skips manual cross-project review, or uses an unsupported recommendation
- **THEN** the field contract SHALL fail
- **AND** candidate generation SHALL remain blocked until the report is regenerated or the script is fixed
