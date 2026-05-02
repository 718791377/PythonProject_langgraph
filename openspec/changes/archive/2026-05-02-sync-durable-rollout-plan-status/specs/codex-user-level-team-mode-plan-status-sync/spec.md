## ADDED Requirements

### Requirement: Durable-state rollout queues SHALL not point at already archived slices as next active work

Bilingual durable-state implementation plans SHALL mark a rollout slice as completed once repository evidence shows the slice has landed, passed validation, and been archived.

#### Scenario: Helper mirror source-of-truth slice has already landed

- **WHEN** the repository contains archived evidence for the helper mirror source-of-truth slice
- **AND** stable specs and tests already verify the helper mirror provenance contract
- **THEN** the cross-session durable-state isolation plan SHALL mark MR 5 as completed
- **AND** it SHALL not continue to describe MR 5 as the next active implementation slice
- **AND** it SHALL identify MR 6 or a bounded MR 6 readiness review as the next decision point
