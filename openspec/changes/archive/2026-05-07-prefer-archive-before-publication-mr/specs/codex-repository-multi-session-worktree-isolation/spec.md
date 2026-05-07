## ADDED Requirements

### Requirement: Completed OpenSpec Changes SHALL Use Archive-Before-Publication Packaging

For a locally completed OpenSpec change that is ready for publication, the repository workflow SHALL archive the change in the same feature branch before opening the GitLab MR.

The resulting publication package SHALL contain the implementation or documentation changes, the archived OpenSpec change directory, and the promoted stable spec updates in one MR.

Two-MR publication is allowed only when the implementation is large or risky, remote CI or MR review should confirm implementation before archive, archive promotion would create heavy stable-spec conflicts, or the user explicitly requests an implementation-only MR.

#### Scenario: Small completed governance change is ready to publish

- **GIVEN** a small governance, documentation, checker, or test change is complete in a feature worktree
- **AND** local implementation validation has passed
- **WHEN** the session prepares a publication recommendation
- **THEN** it SHALL archive the OpenSpec change on the same feature branch before opening the GitLab MR
- **AND** it SHALL re-run local validation after the archive promotes stable specs
- **AND** the MR SHALL include implementation, archive movement, and stable spec updates together

#### Scenario: Two-MR exception is justified

- **GIVEN** the implementation is large or risky
- **OR** remote CI or MR review should confirm implementation before archive
- **OR** archive promotion would create heavy stable-spec conflicts
- **OR** the user explicitly requests an implementation-only MR
- **WHEN** the session recommends publication
- **THEN** it MAY recommend an implementation-only MR first
- **AND** it SHALL state the exception reason
- **AND** it SHALL leave a visible follow-up archive path instead of claiming the OpenSpec lifecycle is closed

#### Scenario: Completed active change reaches main

- **GIVEN** an implementation has already merged to `main`
- **AND** its OpenSpec change is still active with completed tasks
- **WHEN** the repository evaluates OpenSpec lifecycle health
- **THEN** it SHALL treat that state as a lifecycle gap
- **AND** it SHALL prefer an archive follow-up before opening unrelated publication work
