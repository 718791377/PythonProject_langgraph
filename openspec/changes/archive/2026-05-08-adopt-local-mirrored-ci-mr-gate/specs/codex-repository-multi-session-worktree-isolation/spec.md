## ADDED Requirements

### Requirement: Publication SHALL use mirrored local and remote CI/MR gates

Repository publication SHALL use a local-first plus mirrored CI/MR gate.

Feature work SHALL first complete local CI and local MR review from a dedicated feature worktree or feature branch before it is pushed for remote MR review, unless the user explicitly requests an early remote pipeline check.

Local CI and remote CI SHALL reuse the same repository script entrypoint. Remote CI configuration SHALL only install required tools and invoke that shared script; it SHALL NOT maintain a separate divergent checker sequence.

The shared local and remote CI entrypoint SHALL include repository guard checks, whitespace diff checks, and available unit or integration test runners from the repository test surface.

Local MR review SHALL be script-backed and SHALL summarize the feature-branch diff, commit log, diff stat, and merge simulation before remote MR publication. It SHALL fail closed when `git status --porcelain` detects dirty worktree entries unless the operator explicitly performs a non-publication dirty draft review.

Remote MR and remote CI SHALL remain as the remote confirmation and audit-record layer for changes that need remote review.

#### Scenario: Feature branch is ready for remote MR

- **WHEN** a session prepares a feature branch for remote MR review
- **THEN** it SHALL run the shared local CI gate
- **AND** it SHALL run local MR review against the selected base branch
- **AND** it SHALL ask the user whether to push for remote MR review after summarizing both local gate results

#### Scenario: Remote CI runs

- **WHEN** GitLab CI or another remote CI job validates the repository
- **THEN** the remote job SHALL call the same local gate script used by local sessions
- **AND** any local/remote discrepancy SHALL be handled by fixing scripts, environment setup, or configuration drift rather than bypassing either gate

#### Scenario: Low-risk remote deferral

- **WHEN** a low-risk documentation or local draft change does not need remote review immediately
- **THEN** the session MAY recommend waiting before remote publication
- **AND** the recommendation SHALL still preserve local CI and local MR review requirements before any later remote push
