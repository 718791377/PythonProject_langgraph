# Change: Implement Spec Kit Authority Guard R4 Closeout

## Why

The current Spec Kit authority guard already has a dry-run subordinate runtime and focused tests, but the remaining R4 closeout evidence is incomplete. The helper and tests must enforce the strict conflict order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`, and the stable safety-rule spec plus script-backing registry must record that contract before this slice can be considered complete.

## What Changes

- Tighten `tools/spec_kit_subordinate_runtime.py` and `tools/check_spec_kit_authority_guard.py` around the exact priority-order receipt contract.
- Extend focused tests so the runtime receipt must include the strict priority order and the guard rejects receipts that omit it.
- Promote the missing R4 closeout requirement into the stable `codex-user-level-safety-rule-script-backing` spec pair.
- Update the safety-rule script-backing registry and the two Spec Kit implementation plans so `spec_kit_authority_guard_plan` is the owning authority surface and `spec_kit_subordinate_adapter_governance_plan` remains subordinate companion guidance.

## Scope

- `tools/spec_kit_subordinate_runtime.py` - dry-run subordinate runtime helper.
- `tools/check_spec_kit_authority_guard.py` - fail-closed Spec Kit authority checker and receipt validator.
- `test/spec_kit_subordinate_runtime.test.py` - focused runtime receipt contract regression tests.
- `test/spec_kit_authority_guard.test.py` - focused authority-guard and receipt-validation regression tests.
- `openspec/specs/codex-user-level-safety-rule-script-backing/spec.md` - stable English safety-rule requirement.
- `openspec/specs/codex-user-level-safety-rule-script-backing/spec.zh-CN.md` - stable Chinese safety-rule requirement.
- `tools/safety_rule_script_backing_registry.json` - executable-control registry entry for this rule.
- `docs_bilingual/governance/spec_kit_subordinate_adapter_policy.*` - subordinate adapter governance wording.
- `docs_bilingual/implementation_plans/spec_kit_authority_guard_plan.*` - owning implementation-plan wording.
- `docs_bilingual/implementation_plans/spec_kit_subordinate_adapter_governance_plan.*` - companion subordinate-plan wording.

## Non-Goals

- Do not run live `specify`.
- Do not create `.specify/`, root `specs/`, or generated `/speckit.*` / `$speckit-*` surfaces.
- Do not publish GitLab or GitHub changes.

## Rollout

1. Tighten tests first for the strict priority order.
2. Update the runtime helper and guard to satisfy the new test contract.
3. Promote the missing R4 stable-spec and registry closeout.
4. Run focused tests, OpenSpec validation, precommit review, repository guard, local gate, and local MR review.
5. Archive this change on the same feature branch, then merge into local `main` and stop at the remote-publication gate.

## Rollback

- Revert the feature-branch commit or the local `main` merge commit.
- Use the rollback ref created before local integration if local `main` has already moved.
- No user-level runtime state requires rollback because this slice remains dry-run only.

## Verification

- `python test/spec_kit_subordinate_runtime.test.py` - run the focused subordinate-runtime receipt tests.
- `python test/spec_kit_authority_guard.test.py` - run the focused authority-guard tests.
- `python tools/check_spec_kit_authority_guard.py --root . --json` - validate repository surfaces and receipt rules.
- `openspec validate implement-spec-kit-authority-guard-r4-closeout-20260607 --strict` - validate the active closeout change.
- `openspec validate --all` - validate all changes and stable specs.
- `python tools/check_precommit_update_archive.py --root . --json` - confirm update/archive readiness before commit.
- `python tools/run_openspec_guard.py --root .` - run the repository OpenSpec guard.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - run the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - run the local MR review gate.
