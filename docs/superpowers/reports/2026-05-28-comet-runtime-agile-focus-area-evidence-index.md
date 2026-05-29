---
doc_id: comet_runtime_agile_focus_area_evidence_index
lang: en
source_plan: docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md
generated_at: 2026-05-28
---

# Comet Runtime Agile Focus-Area Evidence Index

This report externalizes the historical evidence packages that previously lived inside the active implementation plan.

Source plan: `docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md`

## Term Notes

- `monitor-return-open` - transition that moves the control loop back to Open when Monitoring finds an initiating gap.
- `monitor-return-design` - transition that moves the control loop back to Design when Monitoring finds a planning gap.
- `monitor-return-build` - transition that moves the control loop back to Build when Monitoring finds an execution gap.
- `monitor-return-verify` - transition that moves the control loop back to Verify when Monitoring finds a verification or acceptance gap.
- `iteration_count` - runtime state field that records how many Monitoring return loops have occurred.


## 2026-05-27 Runtime Evidence Batch

- [x] Governance-order package is recorded before non-document runtime execution.
- [x] This batch is classified as script-plus-test implementation, not a new OpenSpec scope.
- [x] No derived `openspec/` or `docs/` update is required for this batch because the active stable spec and governance policy already require management checklist evidence, Monitoring return transitions, and runtime field validation.
- [x] Expected runtime files: `.codex/skills/comet/scripts/comet-state.sh`, `.codex/skills/comet/scripts/comet-guard.sh`, and `.codex/skills/comet/scripts/comet-yaml-validate.sh`.
- [x] Expected evidence files: `test/comet_runtime_management_flow.test.py` and `tools/ci/ci_test_manifest.json`.
- [x] Acceptance evidence must include targeted Comet runtime tests, the OpenSpec Comet/Superpowers policy checker, implementation-plan rules, pre-commit update/archive review, local CI, and local MR review.

## 2026-05-27 Local Execution Governance Package

- [x] This local execution range starts with this `docs_bilingual` package before runtime script and test changes.
- [x] Scope: tighten Comet runtime Monitoring gates for forward transitions, guard diagnostics, archive closing labels, and checker fixtures.
- [x] No derived `openspec/` or `docs/` update is needed in this package because the stable policy and spec already define the management focus-area contract.
- [x] The next commit may modify runtime scripts, targeted tests, and the Comet/Superpowers policy checker fixture only.
- [x] Remote publication remains gated; stop at local `main` unless the user explicitly requests remote publication.

## 2026-05-27 Skill Instruction Alignment Governance Package

- [x] This execution range starts with this `docs_bilingual` package before changing Comet skill instruction files.
- [x] Scope: align operator-facing Comet phase skills with the already implemented management checklist gates, Monitoring return transitions, and non-waterfall adaptive routing.
- [x] This batch is classified as skill-plus-checker implementation; it does not change runtime state-machine behavior.
- [x] No derived `openspec/` or `docs/` update is needed because the stable policy and spec already require checklist evidence, Monitoring return transitions, and adaptive/hybrid control.
- [x] Expected skill files: `.codex/skills/comet-open/SKILL.md`, `.codex/skills/comet-design/SKILL.md`, `.codex/skills/comet-build/SKILL.md`, `.codex/skills/comet-verify/SKILL.md`, `.codex/skills/comet-archive/SKILL.md`, `.codex/skills/comet-hotfix/SKILL.md`, and `.codex/skills/comet-tweak/SKILL.md`.
- [x] Expected checker evidence: `tools/check_openspec_comet_superpowers_policy.py` and `test/run_openspec_guard_json.test.py` if aggregate guard fixture output changes.
- [x] Acceptance evidence must include the Comet/Superpowers policy checker, implementation-plan rules, targeted guard fixture tests, pre-commit update/archive review, local CI, and local MR review.
- [x] Remote publication remains gated; stop at local `main` unless the user explicitly requests remote publication.

## 2026-05-27 Skill Instruction Alignment Evidence

- [x] Comet phase skills now state that Monitoring is cross-cutting and not a sixth Comet phase.
- [x] Comet phase skills now state that forward progression requires `monitoring_status=clear` and `control_decision=continue`.
- [x] Comet phase skills now include return routing for `monitor-return-open`, `monitor-return-design`, `monitor-return-build`, and `monitor-return-verify`.
- [x] `tools/check_openspec_comet_superpowers_policy.py` now enforces per-phase skill instruction terms instead of only checking aggregate skill text.
- [x] `test/run_openspec_guard_json.test.py` now fails when a phase skill loses the Monitoring control-loop instruction.
- [x] Runtime state-machine behavior is unchanged in this batch; no derived `openspec/` or `docs/` update is required.

## 2026-05-27 Root Comet Controller Routing Governance Package

- [x] This local execution range starts with this `docs_bilingual` package before changing the root Comet controller skill or checker code.
- [x] Scope: align `.codex/skills/comet/SKILL.md` phase detection with Monitoring return decisions so the root dispatcher does not force waterfall progression when `control_decision=return-*` is present.
- [x] This batch is classified as root-skill-plus-checker implementation; it does not change runtime state-machine shell behavior.
- [x] No derived `openspec/` or `docs/` update is needed because the stable policy and spec already require adaptive Monitoring return routing and the five-phase Comet contract.
- [x] Expected skill file: `.codex/skills/comet/SKILL.md`.
- [x] Expected checker evidence: `tools/check_openspec_comet_superpowers_policy.py` and `test/run_openspec_guard_json.test.py` should fail if the root Comet skill loses return-dispatch instructions.
- [x] Acceptance evidence must include the Comet/Superpowers policy checker, targeted guard fixture tests, implementation-plan rules, pre-commit update/archive review, local CI, and local MR review.
- [x] Remote publication remains gated; stop at local `main` unless the user explicitly requests remote publication.

## 2026-05-27 Runtime Test Evidence Governance Package

- [x] This local execution range starts with this `docs_bilingual` package before changing targeted runtime tests.
- [x] Scope: strengthen task-level evidence for Monitoring return events, negative return-decision validation, and repeated `iteration_count` increments.
- [x] This batch is classified as test-plus-docs implementation; it does not change Comet runtime shell behavior, policy text, or stable OpenSpec requirements.
- [x] No derived `openspec/` or `docs/` update is needed because this package only proves already-defined runtime behavior with more granular tests.
- [x] Expected test file: `test/comet_runtime_management_flow.test.py`.
- [x] Acceptance evidence must include the targeted Comet runtime management flow test, implementation-plan rules, pre-commit update/archive review, local CI, and local MR review.
- [x] Remote publication remains gated; stop at local `main` unless the user explicitly requests remote publication.

## 2026-05-27 Monitoring Decision Gate Evidence Package

- [x] This local execution range starts with this `docs_bilingual` package before changing targeted runtime tests.
- [x] Scope: add static evidence that Monitoring decisions other than `continue` block forward progress; here `continue` means "current evidence is sufficient to advance," while `adjust-current`, `return-*`, or `stop` means the current phase must be adjusted, returned, or stopped. Archive completion also requires final Monitoring clearance.
- [x] This batch is classified as test-plus-docs implementation; it does not change Comet runtime shell behavior, policy text, stable OpenSpec requirements, or skill instructions.
- [x] No derived `openspec/` or `docs/` update is needed because this package only proves already-defined guard and archive behavior.
- [x] Expected test file: `test/comet_runtime_management_flow.test.py`.
- [x] Acceptance evidence must include the targeted Comet runtime management flow test, implementation-plan rules, pre-commit update/archive review, local CI, and local MR review.
- [x] Remote publication remains gated; stop at local `main` unless the user explicitly requests remote publication.

## 2026-05-28 UTF-8 Management Label Evidence Package

- [x] This local execution range starts with this `docs_bilingual` package before changing Comet runtime scripts and targeted tests.
- [x] Scope: make the Comet runtime management checklist labels readable as UTF-8 Chinese while preserving compatibility with the already supported English labels and existing legacy mojibake labels.
- [x] This batch is classified as script-plus-test implementation; it does not change the Comet phase model, Monitoring transition semantics, stable OpenSpec requirements, or operator-facing skill workflow.
- [x] No derived `openspec/` or `docs/` update is needed because this package only strengthens label compatibility for the existing management-record contract.
- [x] Expected runtime files: `.codex/skills/comet/scripts/comet-state.sh`, `.codex/skills/comet/scripts/comet-guard.sh`, and `.codex/skills/comet/scripts/comet-archive.sh`.
- [x] Expected evidence file: `test/comet_runtime_management_flow.test.py`.
- [x] Acceptance evidence must include the targeted Comet runtime management flow test, implementation-plan rules, pre-commit update/archive review, local MR review, and local CI.
- [x] Remote publication remains gated; stop at local `main` unless the user explicitly requests remote publication.

## 2026-05-28 Management Record Validation Evidence Package

- [x] This local execution range starts with this `docs_bilingual` package before changing Comet runtime validation scripts and targeted tests.
- [x] Scope: make `comet-yaml-validate.sh` fail closed when `management_record` is `null`, empty, or points to a missing file, so every active Comet change keeps durable checklist evidence instead of silently falling back during validation.
- [x] This batch is classified as script-plus-test implementation; it does not change Comet phase semantics, Monitoring return semantics, stable OpenSpec requirements, or operator-facing skill workflow.
- [x] No derived `openspec/` or `docs/` update is needed because the existing stable contract already requires a management record with checklist evidence.
- [x] Expected runtime file: `.codex/skills/comet/scripts/comet-yaml-validate.sh`.
- [x] Expected evidence file: `test/comet_runtime_management_flow.test.py`.
- [x] Acceptance evidence must include the targeted Comet runtime management flow test, implementation-plan rules, pre-commit update/archive review, local MR review, and local CI.
- [x] Remote publication remains gated; stop at local `main` unless the user explicitly requests remote publication.

## 2026-05-28 YAML Enum Validation Evidence Package

- [x] This local execution range starts with this `docs_bilingual` package before changing targeted Comet runtime validation tests.
- [x] Scope: strengthen evidence that `comet-yaml-validate.sh` keeps the managed enum contract described in the Runtime State Contract above; that contract covers workflow kind, current phase, execution mode, isolation mode, verification state, branch handling state, archive flag, monitoring status, control decision, return target, and rework reason.
- [x] This batch is classified as test-plus-docs implementation; it does not change Comet phase semantics, Monitoring return semantics, stable OpenSpec requirements, or operator-facing skill workflow.
- [x] No derived `openspec/` or `docs/` update is needed because the existing stable contract already requires runtime field validation and fail-closed enum handling.
- [x] Expected runtime reference file: `.codex/skills/comet/scripts/comet-yaml-validate.sh`.
- [x] Expected evidence file: `test/comet_runtime_management_flow.test.py`.
- [x] Acceptance evidence must include the targeted Comet runtime management flow test, implementation-plan rules, pre-commit update/archive review, local MR review, and local CI.
- [x] Remote publication remains gated; stop at local `main` unless the user explicitly requests remote publication.

## 2026-05-28 YAML Path Validation Evidence Package

- [x] This local execution range starts with this `docs_bilingual` package before changing targeted Comet runtime validation tests.
- [x] Scope: strengthen evidence that `comet-yaml-validate.sh` validates non-null artifact paths for design documents, implementation plans, and management records, while treating unknown YAML keys as warnings rather than forward-transition blockers.
- [x] This batch is classified as test-plus-docs implementation; it does not change Comet phase semantics, Monitoring return semantics, stable OpenSpec requirements, or operator-facing skill workflow.
- [x] No derived `openspec/` or `docs/` update is needed because the existing stable contract already requires path validation for recorded runtime artifacts.
- [x] Expected runtime reference file: `.codex/skills/comet/scripts/comet-yaml-validate.sh`.
- [x] Expected evidence file: `test/comet_runtime_management_flow.test.py`.
- [x] Acceptance evidence must include the targeted Comet runtime management flow test, implementation-plan rules, pre-commit update/archive review, local MR review, and local CI.
- [x] Remote publication remains gated; stop at local `main` unless the user explicitly requests remote publication.
## 2026-05-28 Verification Report Path Validation Evidence Package
- [x] Local execution scope starts with this `docs_bilingual` governance package, then updates the Comet runtime validator and targeted runtime tests.
- [x] Scope: make `comet-yaml-validate.sh` fail closed when `verification_report` is non-null but points to a missing file, preserving the existing rule that pending phases may keep `verification_report: null`.
- [x] This package is script-plus-test implementation; it does not change Comet phase semantics, Monitoring return semantics, stable OpenSpec requirements, or operator-facing skill workflow.
- [x] This package does not require derived `openspec/` or `docs/` updates because existing stable policy and spec already require verification-report evidence and fail-closed missing-artifact handling.
- [x] Expected runtime file: `.codex/skills/comet/scripts/comet-yaml-validate.sh`.
- [x] Expected evidence file: `test/comet_runtime_management_flow.test.py`.
- [x] Acceptance evidence must include the targeted Comet runtime management flow test, implementation-plan rules, pre-commit update/archive review, local MR review, and local CI.
- [x] Remote publication remains gated; unless the user explicitly requests remote publication, stop at local `main`.
## 2026-05-28 Artifact Path Safety Validation Evidence Package
- [x] Local execution scope starts with this `docs_bilingual` governance package, then updates the Comet runtime validator and targeted runtime tests.
- [x] Scope: make `comet-yaml-validate.sh` fail closed when managed artifact paths are absolute paths or contain path traversal segments, while keeping existing repo-relative artifact paths valid.
- [x] Managed artifact paths in this batch are `design_doc`, `plan`, `verification_report`, and `management_record`.
- [x] This package is script-plus-test implementation; it does not change Comet phase semantics, Monitoring return semantics, stable OpenSpec requirements, or operator-facing skill workflow.
- [x] This package does not require derived `openspec/` or `docs/` updates because existing stable policy and spec already require recorded runtime artifacts and fail-closed missing-artifact handling.
- [x] Expected runtime file: `.codex/skills/comet/scripts/comet-yaml-validate.sh`.
- [x] Expected evidence file: `test/comet_runtime_management_flow.test.py`.
- [x] Acceptance evidence must include the targeted Comet runtime management flow test, implementation-plan rules, pre-commit update/archive review, local MR review, and local CI.
- [x] Remote publication remains gated; unless the user explicitly requests remote publication, stop at local `main`.
