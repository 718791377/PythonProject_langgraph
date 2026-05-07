# codex-repository-multi-session-worktree-isolation Specification

## Purpose
Define how concurrent Codex sessions isolate writable work with dedicated Git worktrees, local ownership claims, and read-only guard scripts so sessions do not overwrite each other or treat unknown dirty files as disposable.
## Requirements
### Requirement: Repository SHALL document multi-session worktree isolation governance

The repository SHALL provide an active bilingual governance policy for multi-session worktree isolation.

At minimum, the policy SHALL define:

- `main` - local branch that mirrors reviewed GitLab mainline.
- `gitlab/main` - remote-tracking reference for the authoritative GitLab mainline.
- `.worktrees/` - local container for secondary Git worktrees.
- `backup/*` - branch namespace for preserving dirty worktree snapshots before risky alignment.

#### Scenario: Cold-start session receives a dirty-file question

- **WHEN** a cold-start Codex session is asked about dirty files, multiple sessions, Git worktrees, local `main`, or GitLab/GitHub sync safety
- **THEN** it SHALL read the multi-session worktree isolation governance policy before recommending cleanup
- **AND** it SHALL not recommend deleting or resetting unknown dirty files before ownership is known

### Requirement: Repository SHALL provide a read-only worktree hygiene checker

The repository SHALL provide `tools/check_worktree_session_hygiene.py` as a read-only checker for multi-session repository hygiene.

The checker SHALL inspect registered Git worktrees and report at least:

- dirty `main` worktree state
- dirty current non-main worktree state
- dirty non-current worktree state
- duplicate dirty paths across worktrees
- local `main` versus `gitlab/main` alignment

#### Scenario: Main worktree is dirty

- **WHEN** the local `main` worktree contains uncommitted changes
- **THEN** the checker SHALL fail
- **AND** the failure SHALL explain that changes must be preserved or moved before aligning `main`

#### Scenario: Current feature worktree is intentionally dirty

- **WHEN** the current worktree is on a non-main feature branch
- **AND** `--allow-current-dirty` is provided
- **THEN** the checker MAY pass for the current worktree dirty state
- **AND** it SHALL still check dirty `main` and duplicate dirty path risks

#### Scenario: Multiple worktrees contain the same dirty path

- **WHEN** two or more registered worktrees contain uncommitted changes to the same repository-relative path
- **THEN** the checker SHALL fail
- **AND** the failure SHALL instruct the operator to serialize ownership before continuing

### Requirement: OpenSpec guard SHALL include worktree hygiene verification

The repository OpenSpec guard SHALL run the worktree hygiene checker.

#### Scenario: Local validation runs before feature-branch commit

- **WHEN** `tools/run_openspec_guard.py` runs locally
- **THEN** it SHALL call `tools/check_worktree_session_hygiene.py` with `--allow-current-dirty`
- **AND** it SHALL still fail when dirty `main` or duplicate dirty path risks are detected

### Requirement: Completed worktree-isolation changes SHALL be archived

Completed OpenSpec changes that add or modify repository multi-session worktree isolation behavior SHALL be archived after implementation and validation so their delta requirements become stable specs.

#### Scenario: Worktree-isolation change is complete

- **WHEN** the governance policy, checker, tests, and guard integration are implemented
- **AND** the change tasks are complete
- **THEN** the change SHALL be archived before the repository treats the work as closed
- **AND** the stable spec SHALL exist under `openspec/specs/`

### Requirement: Sessions SHALL declare active ownership claims before dirty feature work

The repository SHALL provide a local session-ownership claim mechanism for write tasks that may overlap with other Codex sessions.

Claim files SHALL live under `.omx/session-claims/`, which is a local ignored coordination directory and not durable `.omx/state/` runtime truth.

#### Scenario: Dirty feature worktree has no active claim

- **WHEN** a current non-main feature worktree has uncommitted changes
- **AND** the session ownership checker runs with `--allow-current-dirty`
- **AND** no active claim exists for the current worktree
- **THEN** the checker SHALL fail
- **AND** it SHALL explain that the session must declare its OpenSpec change or path ownership before continuing

### Requirement: Session claims SHALL prevent duplicate OpenSpec change ownership

The repository SHALL provide `tools/check_session_ownership_claims.py` as a read-only checker for active session-ownership claims.

The checker SHALL inspect registered Git worktrees and fail when two active claims own the same OpenSpec change.

#### Scenario: Two sessions claim the same OpenSpec change

- **WHEN** two active claim files declare the same OpenSpec change name
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report both claim files so the operator can serialize ownership

### Requirement: Session claims SHALL prevent overlapping hotspot path ownership

The session ownership checker SHALL fail when two active claims declare overlapping repository-relative path scopes.

#### Scenario: Two claims overlap on the same path scope

- **WHEN** one active claim owns `openspec/changes/example`
- **AND** another active claim owns `openspec/changes/example/tasks.md`
- **THEN** the checker SHALL treat the scopes as overlapping
- **AND** it SHALL fail with an operator-facing collision report

### Requirement: OpenSpec guard SHALL include session ownership verification

The repository OpenSpec guard SHALL run the session ownership checker as part of standard local verification.

#### Scenario: Clean CI clone has no local session claims

- **WHEN** `python tools/run_openspec_guard.py --root . --tool codex --json` runs in a clean clone
- **AND** no local `.omx/session-claims/` directory exists
- **THEN** the guard SHALL pass this checker step
- **AND** it SHALL still fail if duplicate active claims are present in registered local worktrees

### Requirement: Session ownership checker SHALL support task ownership precheck

The repository SHALL provide an optional task ownership precheck mode in `tools/check_session_ownership_claims.py`.

The precheck mode SHALL inspect deterministic semantic ownership signals across registered Git worktrees, local branches, remote-tracking branches, active OpenSpec changes, active session claim files, target paths, and ignored/local-only guard-scanned files.

#### Scenario: Matching clean branch claims a task before edits begin

- **WHEN** the checker runs in task ownership precheck mode with a term matching an existing clean feature branch
- **THEN** it SHALL classify the task as `claimed-not-started`
- **AND** it SHALL return a non-zero exit code so a new writer does not create a duplicate work scope silently

#### Scenario: Matching active claim indicates in-progress ownership

- **WHEN** the checker runs in task ownership precheck mode with a target matching an active claim file
- **THEN** it SHALL classify the task as `in-progress`
- **AND** it SHALL report the matching claim file and path or OpenSpec change signal

#### Scenario: Matching ignored guard target is reported

- **WHEN** the checker runs in task ownership precheck mode with a target path or term matching an ignored/local-only file under a guard-scanned directory
- **THEN** it SHALL report that ignored file as an ownership signal
- **AND** it SHALL not delete, move, or modify the file

### Requirement: Task ownership precheck SHALL keep GitLab MR inspection explicit

The task ownership precheck SHALL offer an explicit GitLab MR inspection option without making repository guard execution depend on network access.

#### Scenario: GitLab MR inspection is unavailable but required

- **WHEN** the checker runs in task ownership precheck mode with GitLab MR inspection required
- **AND** the checker cannot inspect open GitLab MRs because token or remote metadata is unavailable
- **THEN** it SHALL fail with an operator-facing error
- **AND** it SHALL leave the repository unchanged

### Requirement: Repository Publication SHALL Prefer Local-First Runner Budgeting

The repository publication workflow SHALL conserve GitLab runner minutes by defaulting to local-first validation and batching before remote push.

#### Scenario: Related local changes are ready for review

- **GIVEN** a maintainer has related changes on one feature branch
- **AND** the changes share one topic, validation surface, and rollback boundary
- **WHEN** local validation passes
- **THEN** the maintainer MAY push the branch once and open or update one GitLab MR
- **AND** the GitLab pipeline remains the merge gate before GitLab `main`

#### Scenario: Unrelated changes would be batched only to save runner minutes

- **GIVEN** two changes have different review topics or rollback boundaries
- **WHEN** a maintainer considers batching them only to reduce GitLab runner-minute usage
- **THEN** the workflow SHALL require separate branches or separate MRs
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

### Requirement: Local Repository SHALL Not Lag The Authoritative Remote Before Work Or Publication

The repository workflow SHALL keep local `main` from lagging behind `gitlab/main` before new writable work, release-timing judgment, push, MR creation, or local alignment claims.

Local-first batching SHALL NOT be used as permission to continue from a stale remote base.

#### Scenario: Local main is behind before writable work

- **GIVEN** `gitlab/main` has advanced
- **AND** local `main` is behind it
- **WHEN** a session prepares to create a new writable task branch
- **THEN** the session SHALL fast-forward local `main` before continuing
- **AND** it SHALL not reset or discard dirty work as part of this freshness check

#### Scenario: Feature branch was prepared on a stale base

- **GIVEN** a local feature branch is ready for release timing judgment
- **AND** refreshed `gitlab/main` shows the feature branch was prepared on a stale base
- **WHEN** the session evaluates publication readiness
- **THEN** it SHALL recommend rebasing or merging onto the refreshed base before publication
- **AND** it MAY proceed from the stale base only if the user explicitly accepts the risk

#### Scenario: Local repository is current

- **GIVEN** refreshed `gitlab/main` matches local `main`
- **WHEN** local validation and release-timing checks pass
- **THEN** the session MAY recommend remote publication
- **AND** GitLab pipeline success remains the merge gate

### Requirement: Legacy Resumed Sessions SHALL Remain Compatibility-Scoped

The repository workflow SHALL treat legacy resumed Codex sessions as compatibility-scoped sessions.

A legacy resumed session is an older Codex `/resume` thread that may retain stale context, stale MCP assumptions, or stale launcher behavior from before the current governance state.

Legacy resumed sessions MAY continue temporarily, but they SHALL NOT override current repository files, current local Git state, active OpenSpec state, or session-ownership claims.

#### Scenario: Old resumed session disagrees with current repository state

- **GIVEN** a legacy resumed session contains stale instructions or stale MCP assumptions
- **WHEN** the session is used for follow-up discussion
- **THEN** the current repository files and current local Git state SHALL be treated as authoritative
- **AND** the old session SHALL NOT claim new governance implementation without revalidating startup summaries, OpenSpec state, Git state, and session-ownership claims

#### Scenario: Old resumed session needs a scoped workaround

- **GIVEN** a legacy resumed session cannot start because of stale runtime or MCP state
- **WHEN** the operator wants to continue that old thread
- **THEN** the session MAY use a per-invocation compatibility override
- **AND** that override SHALL NOT become a permanent global configuration change unless a future approved governance change says so

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
