## 1. OpenSpec Artifacts

- [x] 1.1 Create proposal, design, delta spec, and task artifacts for `upgrade-openspec-comet-superpowers`.
- [x] 1.2 Validate the OpenSpec change status and keep tasks synchronized with implementation.

## 2. Governance Surface

- [x] 2.1 Add `docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md` - English governance policy for the Comet-controlled OpenSpec + Superpowers workflow.
- [x] 2.2 Add `docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.zh-CN.md` - Chinese companion policy.
- [x] 2.3 Register the governance pair in `docs_bilingual/docs_registry.yaml`.

## 3. Checker and Guard Wiring

- [x] 3.1 Add `tools/check_openspec_comet_superpowers_policy.py` - checker for policy files, registry entry, and required workflow boundary terms.
- [x] 3.2 Extend `test/run_openspec_guard_json.test.py` - existing guard JSON test module that now also covers the Comet/OpenSpec/Superpowers checker.
- [x] 3.3 Wire the checker into `tools/run_openspec_guard.py`.

## 4. Validation

- [x] 4.1 Run the new checker and unit test.
- [x] 4.2 Run document governance and OpenSpec validation checks relevant to this change.
- [x] 4.3 Run the precommit update/archive gate and record any remaining blockers.
