## MODIFIED Requirements

### Requirement: Repository SHALL document multi-session worktree isolation governance

The repository SHALL provide an active bilingual governance policy for multi-session worktree isolation.

At minimum, the policy SHALL define:

- `main` - local branch used as the primary local integration surface after approved local validation.
- `gitlab/main` - remote-tracking reference used as an upstream freshness baseline and GitLab publication target.
- `.worktrees/` - local container for secondary Git worktrees.
- `backup/*` - branch namespace for preserving dirty worktree snapshots before risky alignment.

#### Scenario: Cold-start session receives a dirty-file question

- **WHEN** a cold-start Codex session is asked about dirty files, multiple sessions, Git worktrees, local `main`, or GitLab/GitHub sync safety
- **THEN** it SHALL read the multi-session worktree isolation governance policy before recommending cleanup
- **AND** it SHALL not recommend deleting or resetting unknown dirty files before ownership is known

### Requirement: Repository Publication SHALL Prefer Local-First Runner Budgeting

The repository publication workflow SHALL conserve GitLab runner minutes by defaulting to local-first validation, local-main-first integration, and batched remote publication after the local batch is ready.

#### Scenario: Related local changes are ready for review

- **GIVEN** a maintainer has related changes on one feature branch
- **AND** the changes share one topic, validation surface, and rollback boundary
- **WHEN** local validation and local MR review pass
- **THEN** the maintainer MAY recommend integrating the branch into local `main` first after explicit user approval
- **AND** the maintainer MAY publish the resulting local-main commit to GitLab once for remote confirmation and audit

#### Scenario: Unrelated changes would be batched only to save runner minutes

- **GIVEN** two changes have different review topics or rollback boundaries
- **WHEN** a maintainer considers batching them only to reduce GitLab runner-minute usage
- **THEN** the workflow SHALL require separate branches or separate publication packages
- **AND** reviewability and rollback safety SHALL take priority over CI quota savings

#### Scenario: Early remote pipeline is explicitly requested

- **GIVEN** local validation is not yet complete
- **WHEN** the user explicitly requests an early GitLab pipeline check
- **THEN** the maintainer MAY push early
- **AND** the exception SHALL not become the default workflow for routine checkpoints

### Requirement: Release Timing SHALL Be Recommended By The Active Session Before Remote Publication

Before a local batch is pushed to GitLab, the active session's model SHALL judge whether the batch is ready for remote publication and present a publish-or-wait recommendation to the user.

The user SHALL remain the release decision authority.

#### Scenario: Local batch is ready to publish

- **GIVEN** local validation has passed
- **AND** local MR review has passed
- **AND** the active changes are complete or archived
- **AND** the review scope and rollback boundary are coherent
- **WHEN** the active session evaluates release timing
- **THEN** it SHALL recommend either local `main` integration or remote publication according to the current phase
- **AND** it SHALL explain any intentional remote lag between local `main`, `gitlab/main`, and `github/main`

#### Scenario: Local batch should wait

- **GIVEN** local validation has not passed
- **OR** same-topic work is expected immediately
- **OR** the review scope or rollback boundary is unclear
- **WHEN** the active session evaluates release timing
- **THEN** it SHALL recommend waiting
- **AND** it SHALL identify what local work should finish before local `main` integration or remote publication

#### Scenario: User confirms the release decision

- **GIVEN** the active session has presented a publish-or-wait recommendation
- **WHEN** the user confirms local integration or remote publication
- **THEN** the session MAY perform the confirmed action
- **AND** it SHALL not treat GitLab as a required gate before local `main` integration unless the user explicitly chooses that gate for the batch

### Requirement: Completed OpenSpec Changes SHALL Use Archive-Before-Publication Packaging

For a locally completed OpenSpec change that is ready for integration, the repository workflow SHALL archive the change in the same feature branch before local `main` integration or remote publication by default.

The resulting publication package SHALL contain the implementation or documentation changes, the archived OpenSpec change directory, and the promoted stable spec updates in one local integration unit.

Two-step publication is allowed only when the implementation is large or risky, remote CI or remote MR review should confirm implementation before archive, archive promotion would create heavy stable-spec conflicts, or the user explicitly requests an implementation-only publication.

#### Scenario: Small completed governance change is ready to integrate

- **GIVEN** a small governance, documentation, checker, or test change is complete in a feature worktree
- **AND** local implementation validation has passed
- **WHEN** the session prepares an integration recommendation
- **THEN** it SHALL archive the OpenSpec change on the same feature branch before local `main` integration by default
- **AND** it SHALL re-run local validation after the archive promotes stable specs
- **AND** the local integration unit SHALL include implementation, archive movement, and stable spec updates together

#### Scenario: Two-step exception is justified

- **GIVEN** the implementation is large or risky
- **OR** remote CI or remote MR review should confirm implementation before archive
- **OR** archive promotion would create heavy stable-spec conflicts
- **OR** the user explicitly requests an implementation-only publication
- **WHEN** the session recommends publication
- **THEN** it MAY recommend implementation-only publication first
- **AND** it SHALL state the exception reason
- **AND** it SHALL leave a visible follow-up archive path instead of claiming the OpenSpec lifecycle is closed

#### Scenario: Completed active change reaches main

- **GIVEN** an implementation has already merged to `main`
- **AND** its OpenSpec change is still active with completed tasks
- **WHEN** the repository evaluates OpenSpec lifecycle health
- **THEN** it SHALL treat that state as a lifecycle gap
- **AND** it SHALL prefer an archive follow-up before opening unrelated publication work

### Requirement: Feature Worktree Release SHALL Be Separate From Branch Cleanup

The repository SHALL treat a feature worktree as a temporary execution surface and a feature branch as the publication carrier.

A feature worktree MAY be released after local validation passes, all intended tracked changes are committed, `git status` is clean, and untracked or local-only artifacts have been classified. Releasing the worktree SHALL NOT authorize deleting the feature branch.

A feature branch SHALL remain until local `main` contains the branch result and any required GitLab/GitHub remote publication or mirror closure has completed. Local `main` MAY intentionally lead `gitlab/main` and `github/main` during this interval.

#### Scenario: Clean validated worktree is released before remote publication closes

- **GIVEN** a feature worktree is clean
- **AND** local validation has passed
- **AND** tracked, untracked, local evidence, cache, OCR-output, private, copyrighted, and large-file artifacts have been classified
- **WHEN** the operator removes the feature worktree
- **THEN** the repository SHALL keep the feature branch as the publication carrier
- **AND** branch deletion SHALL wait until local `main` integration and any required remote publication or mirror closure are complete

#### Scenario: Hygiene checker reports release and cleanup readiness separately

- **WHEN** the worktree hygiene checker runs
- **THEN** it SHALL report clean feature worktree release candidates
- **AND** it SHALL report branch cleanup readiness separately
- **AND** it SHALL remain read-only

### Requirement: Publication SHALL use mirrored local and remote CI/MR gates

Repository publication SHALL use local-first validation plus mirrored local and remote CI/MR gates.

Feature work SHALL first complete local CI and local MR review from a dedicated feature worktree or feature branch before local `main` integration or remote publication, unless the user explicitly requests an early remote pipeline check.

Local CI and remote CI SHALL reuse the same repository script entrypoint. Remote CI configuration SHALL only install required tools and invoke that shared script; it SHALL NOT maintain a separate divergent checker sequence.

The shared local and remote CI entrypoint SHALL include repository guard checks, whitespace diff checks, and available unit or integration test runners from the repository test surface.

Local MR review SHALL be script-backed and SHALL summarize the feature-branch diff, commit log, diff stat, and merge simulation before local `main` integration or remote publication. It SHALL fail closed when `git status --porcelain` detects dirty worktree entries unless the operator explicitly performs a non-publication dirty draft review.

Remote MR and remote CI SHALL remain as clean-environment confirmation, permission, backup, and audit-record layers for changes that need remote review.

#### Scenario: Feature branch is ready for local integration

- **WHEN** a session prepares a feature branch for local `main` integration
- **THEN** it SHALL run the shared local CI gate
- **AND** it SHALL run local MR review against the selected base branch
- **AND** it SHALL ask the user whether to integrate locally after summarizing both local gate results

#### Scenario: Remote CI runs

- **WHEN** GitLab CI or another remote CI job validates the repository
- **THEN** the remote job SHALL call the same local gate script used by local sessions
- **AND** any local/remote discrepancy SHALL be handled by fixing scripts, environment setup, or configuration drift rather than bypassing either gate

#### Scenario: Low-risk remote deferral

- **WHEN** a low-risk documentation or local draft change does not need remote review immediately
- **THEN** the session MAY recommend waiting before remote publication
- **AND** the recommendation SHALL still preserve local CI and local MR review requirements before any later local integration or remote push

## REMOVED Requirements

### Requirement: Local Repository SHALL Not Lag The Authoritative Remote Before Work Or Publication

**Reason**: The old heading treated GitLab as the authority for the local repository, which conflicts with the requested local-main-first workflow.

**Migration**: Use `Local Main SHALL Use Fresh Remote Baselines While Allowing Publication Lag`, which preserves stale-upstream protection while allowing local `main` to lead remotes after approved local integration.

## ADDED Requirements

### Requirement: Local Main SHALL Use Fresh Remote Baselines While Allowing Publication Lag

The repository workflow SHALL keep local `main` from starting new writable work or publication judgment from a stale upstream baseline, while allowing local `main` to intentionally lead `gitlab/main` and `github/main` after approved local integration.

The primary directory `D:\PythonProject_langgraph` SHALL be the primary main worktree. It SHALL be checked out on local `main`, SHALL NOT lag behind the local `main` branch reference, and normally SHOULD exactly equal the local `main` branch reference.

Local-first batching SHALL NOT be used as permission to continue from a stale remote base. Local-main-first integration MAY intentionally create remote lag, and that lag SHALL be reported until cleared.

#### Scenario: Local main is behind before writable work

- **GIVEN** `gitlab/main` has advanced
- **AND** local `main` is behind it
- **WHEN** a session prepares to create a new writable task branch
- **THEN** the session SHALL fast-forward local `main` before continuing unless the user explicitly accepts stale-base risk
- **AND** the worktree hygiene checker SHALL fail until local `main` is no longer behind `gitlab/main`
- **AND** it SHALL not reset or discard dirty work as part of this freshness check

#### Scenario: Primary main worktree is not on local main

- **GIVEN** the primary directory `D:\PythonProject_langgraph` is not checked out on local `main`
- **WHEN** the worktree hygiene checker runs
- **THEN** the checker SHALL fail
- **AND** the session SHALL stop writable work until the primary directory hygiene issue is resolved

#### Scenario: Primary main worktree is behind local main

- **GIVEN** the primary directory `D:\PythonProject_langgraph` is checked out on local `main`
- **AND** its HEAD differs from the local `main` branch reference
- **WHEN** the worktree hygiene checker runs
- **THEN** the checker SHALL fail
- **AND** the failure SHALL instruct the operator to check out or fast-forward the primary directory to local `main`

#### Scenario: Local main is ahead of gitlab main

- **GIVEN** refreshed `gitlab/main` is an ancestor of local `main`
- **WHEN** the worktree hygiene checker runs
- **THEN** the checker SHALL treat local `main` as not behind `gitlab/main`
- **AND** it SHALL report that remote publication lag is allowed when intentional
- **AND** it SHALL remind the operator not to use the primary `main` worktree for feature work

#### Scenario: Feature branch was prepared on a stale base

- **GIVEN** a local feature branch is ready for local integration or release timing judgment
- **AND** refreshed `gitlab/main` shows the feature branch was prepared on a stale base
- **WHEN** the session evaluates readiness
- **THEN** it SHALL recommend rebasing or merging onto the refreshed base before integration or publication
- **AND** it MAY proceed from the stale base only if the user explicitly accepts the risk

#### Scenario: Local main intentionally leads remotes

- **GIVEN** local `main` contains an approved local integration
- **AND** `gitlab/main` or `github/main` does not yet contain that commit
- **WHEN** a session reports repository state
- **THEN** it SHALL identify the remote-lag state explicitly
- **AND** it SHALL not treat that state as a failure by itself
