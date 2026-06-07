# Tasks

## 1. RED tests
- [x] Add focused tests for checker findings, protected spans, runtime analyze/rewrite/apply guards, and R4 smoke receipts.
- [x] Run the focused test and confirm it fails before production code exists.

## 2. Runtime and checkers
- [x] Implement `tools/check_stop_slop_caveman_response_density.py`.
- [x] Implement `tools/stop_slop_caveman_runtime.py`.
- [x] Implement `tools/check_stop_slop_caveman_smoke_receipts.py`.

## 3. Registration and documentation
- [x] Register focused tests in `tools/ci/ci_test_manifest.json`.
- [x] Register checker wiring in `tools/run_openspec_guard.py`.
- [x] Register safety-rule backing in `tools/safety_rule_script_backing_registry.json`.
- [x] Update the bilingual implementation plan status, tasks, and evidence.

## 4. Verification and local integration
- [x] Run focused tests and smoke checker/runner evidence.
- [x] Run OpenSpec strict validation.
- [x] Run OpenSpec guard after the active shared-hotspot ownership claims are serialized.
- [x] Run precommit update/archive review after the OpenSpec guard blocker is cleared.
- [x] Archive the completed OpenSpec change and rerun validation.
- [ ] Commit with Chinese subject, run local gate and local MR review.
- [ ] Merge into local `main`, cleanup integrated worktree/branch, and stop at remote-publication gate.
