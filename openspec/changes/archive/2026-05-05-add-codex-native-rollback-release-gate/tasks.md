## 1. OpenSpec Artifacts

- [x] 1.1 Create proposal and design artifacts for the Codex native preservation and rollback release gate.
- [x] 1.2 Add delta requirements for release-gate evidence in team-mode controls and startup binding specs.
- [x] 1.3 Add Chinese companion artifacts for the manually maintained OpenSpec Markdown files.

## 2. Release Gate Template And Checker

- [x] 2.1 Add `tools/codex_native_rollback_release_gate_template.json` - the JSON release-gate template for native Codex preservation and rollback evidence.
- [x] 2.2 Add `tools/check_codex_native_rollback_release_gate_template.py` - the static checker for the release-gate template and repository evidence.
- [x] 2.3 Wire the new checker into `tools/run_openspec_guard.py` - the aggregate OpenSpec guard script.

## 3. Documentation And Validation

- [x] 3.1 Update the active user-level team-mode implementation plan with the new release-gate slice.
- [x] 3.2 Update the long-term production durable-team draft with the same release-gate boundary.
- [x] 3.3 Run the release-gate checker, installer rollback test, OpenSpec validation, and aggregate OpenSpec guard.
