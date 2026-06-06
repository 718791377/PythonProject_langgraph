# Tasks

## 1. OpenSpec and design

- [x] 1.1 Create the bounded OpenSpec change package for durable smoke R4 runtime.
- [x] 1.2 Document the helper-only design and non-adoption boundary.

## 2. Runtime and checker

- [x] 2.1 Add a read-only durable routing smoke runner that writes an explicit R4 receipt path.
- [x] 2.2 Add fail-closed receipt validation for timeout release, rollback readiness, transcript redaction, backend-family evidence, and non-adoption fields.
- [x] 2.3 Add focused tests for valid smoke receipts, adoption-claim rejection, transcript bounds, runner success, and unsafe apply-command rejection.

## 3. Registration and documentation

- [x] 3.1 Register the new checker in the OpenSpec guard JSON and non-JSON paths.
- [x] 3.2 Register the new test in the CI manifest.
- [x] 3.3 Update the durable smoke/adoption implementation plan and stable spec pair.

## 4. Validation and local integration

- [x] 4.1 Run focused tests, receipt checker, runner smoke, and receipt validation.
- [x] 4.2 Run OpenSpec validation; precommit update/archive review and repository guard remain post-archive gates.
- [x] 4.3 Archive the completed OpenSpec change and rerun validation.
- [ ] 4.4 Run local gate and local MR review on a clean feature worktree.
- [ ] 4.5 Merge into local `main`, run post-merge validation, cleanup integrated feature worktree/branch, and stop at the remote-publication gate.
