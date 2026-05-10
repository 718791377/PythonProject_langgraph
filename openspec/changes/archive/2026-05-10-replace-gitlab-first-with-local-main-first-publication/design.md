## Context

The previous publication model used local-first batching but still made GitLab the authoritative review and merge surface. That meant local validation happened first, but the result did not enter `main` until after GitLab MR/pipeline/merge. The user now wants the opposite authority order for this repository: local validation and user approval may integrate the result into local `main` first, while remotes can temporarily lag.

## Decisions

### Decision 1: Local `main` is the primary integration surface

After feature work is complete, local CI and local MR review pass, the feature worktree is clean, and the user approves integration, the feature branch may be fast-forwarded or otherwise integrated into local `main` before GitLab has accepted the change.

Why:

- It satisfies the explicit local-first request.
- It lets local `main` represent the operator-approved state even while remote CI/MR is pending.
- It removes the old GitLab-first authority inversion.

### Decision 2: Remote lag is allowed but must be visible

When local `main` leads `gitlab/main` or `github/main`, sessions must report that state as intentional remote lag, keep the publication carrier branch until remote closure, and later clear the lag through GitLab/GitHub publication or sync.

Why:

- The user explicitly allows remotes to lag.
- Visibility prevents future sessions from mistaking local-ahead state for accidental drift.

### Decision 3: Stale upstream bases are still unsafe

Before new writable work, release-timing judgment, remote push/MR creation, or mainline-state claims, sessions still refresh `gitlab/main`. If remote has advanced beyond local `main`, local `main` must be fast-forwarded or the user must explicitly accept stale-base risk.

Why:

- Local-main-first does not mean ignoring newer reviewed work from the remote.
- This preserves the safety value of existing freshness checks while allowing local ahead-of-remote states after local integration.

### Decision 4: GitLab/GitHub remain publication and audit surfaces

GitLab CI/MR and GitHub sync remain useful clean-environment, backup, permission, and audit/mirror surfaces. They are no longer the default gate before a validated local result can enter local `main`.

Why:

- Removing GitLab-first should not remove remote verification or backups.
- Existing remote CI can keep reusing `tools/ci/local_gate.ps1` to detect environment drift.

## Migration Notes

- Replace active policy wording that says GitLab is authoritative with local-main-first wording.
- Replace exact `GitLab-first` references in active docs/specs with `local-main-first` or historically specific neutral wording.
- Keep archived OpenSpec records as historical evidence unless they are promoted stable specs or active startup/governance surfaces.
- Update checker messages/help to call `gitlab/main` a remote publication baseline rather than an authoritative mainline target.

## Risks / Trade-offs

- Risk: local `main` may be ahead of remotes for longer than intended. Mitigation: status reports must call out remote lag and branch cleanup remains blocked until remote/mirror closure.
- Risk: local integration without remote green could hide clean-environment failures. Mitigation: local gates remain mandatory, and remote CI remains a later confirmation surface that must be reconciled if it disagrees.
- Risk: future sessions may confuse local `main` with a feature workspace. Mitigation: feature implementation still happens only in feature branches/worktrees; local `main` is integration-only.
