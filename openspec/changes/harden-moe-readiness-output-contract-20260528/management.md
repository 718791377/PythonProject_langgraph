# Management Checklist

## Open

- [x] Value/why evidence checked: GUI preflight needs stable top-level readiness evidence fields.
- [x] Success criteria evidence checked: output fields, regression assertions, and plan checklist update.
- [x] Stakeholders/constraints checked: Codex operator, target projects, local-first policy, and no remote publication authorization.

## Design

- [x] Delivery tailoring checked: bounded feature worktree slice; no real target writes.
- [x] Risks and assumptions checked: additive output fields must not change existing lane semantics.
- [x] Acceptance evidence path checked: targeted tests, OpenSpec validation, repository guard, local gate, and local MR review.

## Build

- [ ] Implement derived readiness output contract fields.
- [ ] Add regression assertions.
- [ ] Update plan checklist from evidence.

## Verify

- [ ] Run targeted tests and repository gates.
- [ ] Run local gate and local MR review.
- [ ] Check control decision before local main integration.

## Monitoring

- [x] Current facts checked: local `main` is ahead of GitLab and this slice has no remote-publication authorization.
- [x] Return/no-return decision checked: bounded implementation can proceed from Build.

## Archive

- [x] Archive/sync evidence deferred in `.openspec.yaml` until post-integration closure.
