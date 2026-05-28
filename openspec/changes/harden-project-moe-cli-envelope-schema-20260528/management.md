# Management Checklist

## Open

- [x] Value/why evidence checked: unsupported target Mode CLI envelope schema must fail closed before GUI control.
- [x] Success criteria evidence checked: stable blocker, targeted regression test, implementation-plan evidence update, and local validation.
- [x] Stakeholders/constraints checked: Codex operator, target projects, local-first publication policy, and no remote publication authorization.

## Design

- [x] Delivery tailoring checked: small tweak slice in a feature worktree; no real target-project writes.
- [x] Risks and assumptions checked: schema mismatch is a compatibility blocker and must not be treated as ready.
- [x] Acceptance evidence path checked: targeted tests, OpenSpec validation, repository guard, local gate, and local MR review.

## Build

- [x] Execution mode checked: main session executes a single bounded slice in a dedicated worktree.
- [x] Quality evidence checked: blocker catalog, shared envelope validator, regression test, and plan checklist remain synchronized.
- [x] Blocker decision checked: Comet bash is unavailable on this Windows surface, so repository/OpenSpec gates are used as fallback evidence.

## Verify

- [ ] Variance review checked after tests and gates complete.
- [ ] Risk/change impact checked after local MR review.
- [ ] Control decision checked before local main integration.

## Monitoring

- [x] Current facts checked: local `main` is clean and ahead of GitLab; no durable-team threshold is met for this single slice.
- [x] Return/no-return decision checked: the slice has a bounded implementation plan and does not need a return to Open/Design.

## Archive

- [x] Value outcome will be checked after local integration evidence is available.
- [x] Lessons learned will be recorded in the final verification/cleanup report if needed.
- [x] Archive/sync evidence deferred in `.openspec.yaml` until post-integration closure.
