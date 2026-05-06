## ADDED Requirements

### Requirement: Release Timing SHALL Be Recommended By The Active Session Before Remote Publication

Before a local batch is pushed to GitLab, the active session's model SHALL judge whether the batch is ready for remote publication and present a publish-or-wait recommendation to the user.

The user SHALL remain the release decision authority.

#### Scenario: Local batch is ready to publish

- **GIVEN** local validation has passed
- **AND** the active changes are complete or archived
- **AND** the review scope and rollback boundary are coherent
- **WHEN** the active session evaluates release timing
- **THEN** it SHALL recommend publishing to the user
- **AND** it SHALL explain why the runner-minute cost is justified

#### Scenario: Local batch should wait

- **GIVEN** local validation has not passed
- **OR** same-topic work is expected immediately
- **OR** the review scope or rollback boundary is unclear
- **WHEN** the active session evaluates release timing
- **THEN** it SHALL recommend waiting
- **AND** it SHALL identify what local work should finish before remote publication

#### Scenario: User confirms the release decision

- **GIVEN** the active session has presented a publish-or-wait recommendation
- **WHEN** the user confirms publishing
- **THEN** the session MAY push to GitLab and open or update the MR
- **AND** the GitLab pipeline remains the merge gate
