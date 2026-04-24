## ADDED Requirements

### Requirement: Canonical implementation-plan documents SHALL distinguish current implementation reality from future direction
When a canonical implementation-plan document is used as an operator-facing state map, it SHALL distinguish current implementation reality from optional future direction rather than blending them into one roadmap layer.

#### Scenario: A plan document contains both implemented and future sections
- **WHEN** a canonical implementation-plan document includes both current surfaces and future extensions
- **THEN** it SHALL mark those states distinctly
- **AND** it SHALL avoid presenting future-only items as if they were already part of the current default operator path
