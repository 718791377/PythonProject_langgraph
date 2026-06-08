# Tasks

## 1. OpenSpec and design

- [x] 1.1 Create the bounded OpenSpec change package for gstack Codex delivery-loop runtime R4.
- [x] 1.2 Document the strict conflict-priority boundary and implemented-local R0-R4 scope.

## 2. Runtime and checker

- [x] 2.1 Add the repo-local gstack delivery-loop runtime helper with dry-run actions and bounded R4 smoke receipts.
- [x] 2.2 Add the fail-closed checker for priority evidence, receipt validation, and guard/CI registration.
- [x] 2.3 Keep the runtime helper advisory-only and non-mutating outside the explicit smoke receipt path.

## 3. Tests and registration

- [x] 3.1 Add focused tests for dry-run output, blocked smoke receipts, positive smoke receipts, forbidden live/write markers, and redaction.
- [x] 3.2 Register the new tests in `tools/ci/ci_test_manifest.json`.
- [x] 3.3 Register the checker in `tools/run_openspec_guard.py` and `tools/safety_rule_script_backing_registry.json`.

## 4. Documentation and spec sync

- [x] 4.1 Update the gstack child plan and parent plan to reflect the implemented-local R0-R4 boundary.
- [x] 4.2 Add a dedicated stable spec delta for the gstack delivery-loop runtime governance lane.

## 5. Validation and archive

- [x] 5.1 Run focused tests and the gstack checker.
- [x] 5.2 Run `python tools/check_precommit_update_archive.py --root . --json` and `python tools/run_openspec_guard.py --root . --json`.
- [x] 5.3 Archive the completed OpenSpec change and rerun OpenSpec validation.
- [x] 5.4 Run local gate and local MR review from a clean feature worktree.
