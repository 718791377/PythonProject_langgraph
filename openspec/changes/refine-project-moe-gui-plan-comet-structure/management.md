# Management Checklist

## Open

- [x] Value/why evidence checked: the previous structure needed full Comet trace and state-boundary clarification.
- [x] Success criteria evidence checked: target file has Comet structure, OpenSpec artifacts, design doc, implementation plan, validation path.
- [x] Stakeholders/constraints checked: Codex operator, future Project MOE GUI implementers, target projects, local-first publication policy.

## Design

- [x] Delivery tailoring checked: documentation-only change, feature worktree isolation, no runtime/user-level writes.
- [x] Risks and assumptions checked: target project readiness must not be overstated; Comet bash unavailable is recorded.
- [x] Acceptance evidence path checked: validation commands listed in proposal/tasks/target plan.

## Build

- [x] Execution mode checked: `executing-plans` in a dedicated worktree.
- [x] Quality evidence checked: repository-local validation commands are required before commit.
- [x] Blocker decision checked: Comet bash is unavailable and handled by fallback evidence plus archive deferral.

## Verify

- [x] Variance review checked: no runtime code, dependency install, target write or remote publication included.
- [x] Risk/change impact checked: documentation/OpenSpec-only impact.
- [x] Control decision checked: continue to local feature commit after validation.

## Monitoring

- [x] Current facts checked: active change exists; feature worktree created; no durable team threshold met.
- [x] Return/no-return decision checked: no return to Open/Design required for this scoped refactor.

## Archive

- [x] Value outcome checked for deferral: plan structure becomes implementation-slicing ready.
- [x] Lessons learned checked: Windows Comet `.sh` scripts must not be claimed as executed without bash.
- [x] Archive/sync evidence deferred: `.openspec.yaml` records `x_archive_deferred_reason` and `x_archive_follow_up`.
