# Design: Local not-behind-remote rule

## Rule Shape

Local-first batching reduces remote pipeline frequency, but it must not create stale-base work. Before a new writable task, release-timing judgment, push, MR creation, or local alignment claim, the session must refresh `gitlab/main` and verify local `main` is not behind it.

## Stale Feature Branch Handling

If the feature branch was prepared on a stale base, the branch must be rebased or merged onto the refreshed base before publication unless the user explicitly accepts the stale-base risk.

## Safety Boundary

The rule does not authorize destructive cleanup. Dirty work still follows preservation-first classification before any reset, checkout, clean, move, or delete operation.
