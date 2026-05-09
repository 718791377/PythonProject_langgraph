## MODIFIED Requirements

### Requirement: Governance checks SHALL classify errors, warnings, and deferred cleanup separately

The skills governance validation surface SHALL distinguish blocking errors, non-blocking warnings, and deferred cleanup candidates.

Blocking errors MUST include missing required repository artifacts, same-layer user or repository-local duplicate skills not covered by policy, unknown profile tags, and broken documentation registry coverage. Warnings MAY include known cross-layer duplicates, plugin-layer duplicate skill names, known plugin bundle limitations, known Vercel bulk-load behavior, and user-level long descriptions that are intentionally not edited in the current phase. Deferred cleanup MUST include candidates that require future clean-clone evidence.

#### Scenario: Validation reports a blocking defect
- **WHEN** a required repository-local artifact or registry entry is missing
- **THEN** the governance check SHALL report an error
- **AND** the affected lifecycle phase SHALL not be accepted until the defect is fixed

#### Scenario: Validation reports an expected non-blocking issue
- **WHEN** the check detects a known user-level long description, a plugin-layer duplicate skill name, or known plugin bundle limitation
- **THEN** the governance check SHALL report a warning
- **AND** it SHALL not rewrite user-level or plugin-managed files as part of reporting that warning

#### Scenario: Validation reports cleanup candidates
- **WHEN** the check detects duplicate files that require OpenSpec regeneration evidence before removal
- **THEN** the governance check SHALL report the candidate as deferred cleanup
- **AND** it SHALL not treat the candidate as permission to delete files
