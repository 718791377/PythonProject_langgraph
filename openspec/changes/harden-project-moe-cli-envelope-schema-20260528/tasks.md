# Tasks

## 1. OpenSpec package

- [x] 1.1 Create the bounded OpenSpec change package for Project MOE CLI envelope schema hardening.
- [x] 1.2 Record local-only scope, rollback, validation path, and archive deferral.

## 2. Implementation

- [x] 2.1 Add a stable `blocked:cli_envelope_schema_version_mismatch` blocker and remediation metadata.
- [x] 2.2 Reject unsupported target Mode CLI envelope `schema_version` values in the shared read-contract validator.
- [x] 2.3 Add a Phase 1 readiness regression test for unsupported read-contract envelope schema.
- [x] 2.4 Update the Project MOE GUI implementation-plan checklist for the covered readiness evidence.

## 3. Validation and local integration

- [x] 3.1 Run targeted Project MOE GUI toolchain tests.
- [x] 3.2 Run OpenSpec validation, precommit update/archive review, and repository guard.
- [ ] 3.3 Run local gate and local MR review on the clean feature worktree.
- [ ] 3.4 Create a rollback ref, merge into local `main`, run post-merge local gate, and clean the integrated worktree/branch.
