# Change: Enforce remote publication approval gate

## Why
The local-main-first workflow intentionally allows local `main` to lead GitLab and GitHub after approved local integration. A recent execution showed that existing policy wording and checks were not fail-closed enough: after local main integration, a generic "continue" was treated as permission to push a GitLab MR, merge it, sync GitHub, and clean the publication branch.

Remote publication changes external state, consumes remote CI, and closes the mirror loop. It must require a fresh, explicit remote-publication approval instead of inheriting approval for local integration or interpreting generic continuation as publication authorization.

## What Changes
- Strengthen publication policy/spec wording so local integration approval and remote publication approval are separate decisions.
- Require a fresh explicit user approval before GitLab push/MR, GitLab merge, GitHub sync, or remote source-branch deletion.
- Add a script-backed checker that verifies the approval boundary is present across policy/spec/startup surfaces and registered in the guard.
- Add regression tests proving missing approval-gate wording fails.

## Impact
- Static policy/checker enforcement only.
- Does not push remotes, create MRs, merge remote branches, or mutate remote refs.
- Future remote publication should be performed only after the session presents a publish-or-wait recommendation and receives explicit remote-publication approval.