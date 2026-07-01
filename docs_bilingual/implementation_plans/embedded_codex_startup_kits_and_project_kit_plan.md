---
doc_id: embedded_codex_startup_kits_and_project_kit_plan
doc_class: implementation_plan
status: final
canonical_path: docs_bilingual/implementation_plans/embedded_codex_startup_kits_and_project_kit_plan.md
zh_cn_path: docs_bilingual/implementation_plans/embedded_codex_startup_kits_and_project_kit_plan.zh-CN.md
---
# Embedded Codex Startup Kits And Project Kit Plan

## Purpose

Freeze the implementation contract for the next operations-package layer after the 48 Codex durable-team body documents, the 60 one-person-company body documents, and the embedded-governance alignment checker. The new layer turns the existing body packages into startup-ready, reusable, auditable operating kits without changing the truth boundary: the one-person company owns business truth, and the embedded Codex durable team owns execution truth.

## Stage A Boundary

Stage A is this frozen implementation plan plus registry registration only. It is a docs-only governance confirmation package. It must land on local `main` before Stage B starts. Stage A does not create templates, project-kit files, runtime checkers, tests, or generated package changes.

## Stage B Output Set

Stage B must add these bilingual document groups:

1. Codex minimum startup documents list:
   - `docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.md` - defines the English canonical Codex startup order.
   - `docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.zh-CN.md` - mirrors the Codex startup order for Chinese operators.
2. One-person-company embedded Codex startup matrix:
   - `docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.md` - maps business startup documents to embedded Codex governance surfaces.
   - `docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.zh-CN.md` - mirrors the embedded startup matrix for Chinese operators.
3. Shared governance ledger templates under `docs_bilingual/templates/shared_governance_ledgers/`:
   - `decision-log-entry-template.md` - captures scoped decisions with truth-owner metadata.
   - `risk-register-entry-template.md` - captures business, Codex, and mixed risks with evidence links.
   - `experiment-log-entry-template.md` - records market, product, and automation experiments.
   - `learning-log-entry-template.md` - preserves validated business and platform learning.
   - `human-review-record-template.md` - records required human review before commitments or release gates.
   - `monthly-review-template.md` - structures monthly review across business and platform loops.
   - each with a `.zh-CN.md` companion.
4. Tailoring decision record template:
   - `docs_bilingual/templates/tailoring_decision_record_template.md` - records why a full, light, or module-tailored operating mode was chosen.
   - `docs_bilingual/templates/tailoring_decision_record_template.zh-CN.md` - mirrors tailoring-decision fields for Chinese operators.
5. One-person-company with embedded Codex project kit under `docs_bilingual/project_kits/one_person_company_with_embedded_codex/`:
   - `README.md` - orients operators to the embedded one-person-company project kit.
   - `startup-checklist.md` - gives the first-run checklist for business and Codex gates.
   - `folder-structure.md` - explains where business, Codex, shared, and runtime evidence files live.
   - `governance-gates.md` - defines business gates, Codex execution gates, and mixed two-gate review.
   - `local-main-workflow.md` - documents the local-main-first validation and merge workflow.
   - `remote-publication-gate.md` - defines the stop point before GitLab or GitHub publication.
   - `monthly-review-sample.md` - shows a sample review that joins business learning with platform evidence.
   - each with a `.zh-CN.md` companion.

Stage B must also update `docs_bilingual/docs_registry.yaml` for every new bilingual pair.

## Stage B Runtime Contract

Stage B must add a focused checker:

```powershell
python .\tools\check_embedded_codex_startup_kits.py --root . --json
```

The checker must fail closed when:

- the Codex 12-document startup list is missing or has a different canonical order;
- the embedded startup matrix lacks business, codex, mixed, truth owner, evidence source, decision right, linked docs, or two-gate language;
- shared ledger templates do not expose `scope`, `truth_owner`, `evidence_source`, `decision_right`, and `linked_docs`;
- the tailoring record template lacks mode, why-not-heavier, why-not-lighter, escalation triggers, rollback, and local-main evidence fields;
- the project kit misses startup checklist, folder structure, governance gates, local-main workflow, remote-publication gate, or monthly review sample;
- registry entries are missing, duplicated, unpaired, or point to missing files;
- any new English primary contains non-ASCII text, or any zh-CN companion is invalid UTF-8;
- the checker test is not registered in `tools/ci/ci_test_manifest.json`;
- the checker is not registered in `tools/run_openspec_guard.py` and `tools/safety_rule_script_backing_registry.json`.

## Required Codex Minimum Startup Order

The Codex startup list is frozen in this order:

1. `thesis.md` - explains why the embedded Codex platform capability exists.
2. `architecture.md` - defines execution architecture and authority boundaries.
3. `agent-governance.md` - defines what agents may do, draft, or escalate.
4. `agent-role-map.md` - maps agent roles to operating responsibilities.
5. `agent-permissions.md` - defines tool, data, and approval permissions.
6. `delivery-plan.md` - defines how Codex work moves through delivery gates.
7. `observability.md` - defines runtime, repo, and agent evidence signals.
8. `risk-register.md` - records platform, business, and mixed operating risks.
9. `human-review-checklist.md` - defines human review before commitments and releases.
10. `decision-log.md` - records decisions with scope and truth-owner fields.
11. `backup-restore.md` - defines recovery for repo, runtime, and durable state evidence.
12. `monthly-review.md` - drives recurring platform and business learning review.

This list is not a business-startup list. It is the minimum embedded platform-governance start set for agents, worktrees, durable state, validation gates, release gates, evidence, rollback, and review.

## Required Startup Matrix Contract

The startup matrix must map:

- one-person-company startup document;
- embedded Codex startup document;
- shared ledger, when the row uses a shared truth surface;
- `scope: business | codex | mixed`;
- `truth_owner: founder | codex-operator | human-review`;
- `evidence_source: customer | revenue | repo | runtime | agent | legal`;
- `decision_right: human | delegated-draft-only`;
- two-gate trigger and escalation note.

It must explicitly state that mixed customer/revenue/compliance plus code/agent/runtime work requires both the business gate and the Codex execution gate.

## Required Process-Group Style

Execution-facing new files must include process-group language. When a file prescribes operating behavior, it must include sections or tables for Inputs, Tools And Techniques, and Outputs. Chinese companions must include equivalent input, tools-and-techniques, and output headings.

## Verification Plan

Stage B must run at minimum:

```powershell
python .\tools\check_embedded_codex_startup_kits.py --root . --json
python .\tools\ci\run_python_tests.py --root . --pattern check_embedded_codex_startup_kits.test.py
python .\tools\check_embedded_codex_governance_alignment.py --root . --json
python .\tools\check_operations_package_docs.py --root . --json
python .\tools\check_precommit_update_archive.py --root . --json
```

Before Stage B local-main integration, run local MR review and the broad local gate when not blocked by a pre-existing unrelated external plugin/cache issue. If the broad gate is blocked by such a pre-existing issue, record the blocker and rely on the focused checker/test chain plus local MR review for this package.

## Local Integration And Publication Boundary

Stage A and Stage B use local-main-first integration. A clean feature worktree, focused validation, local MR review, rollback ref, and completed claim are required before declaring completion. Remote publication is not authorized by this plan: do not push GitLab, create or update GitLab MRs, merge GitLab MRs, sync GitHub, delete remote refs, or mutate any remote publication state.

## Current Status

<!-- CURRENT_STATUS_START -->
- Stage A freezes the startup kits and project-kit implementation contract.
- Stage B is pending until this plan is merged into local `main` and the current user implementation request is recorded as the implementation confirmation.
- Durable-team threshold is re-evaluated for Stage B because Stage B has independent docs/template and checker/test slices; native expert assistance may be used with leader-owned fan-in.
- Remote publication is not authorized.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Completed in Stage A: freeze this implementation plan and register it.
- Pending for Stage B: create the Codex minimum startup list and embedded startup matrix.
- Pending for Stage B: create shared ledger templates, tailoring record template, and project kit files.
- Pending for Stage B: add checker, tests, guard registration, CI manifest registration, safety-rule registry entry, and docs registry entries.
- Pending for Stage B: validate, commit, integrate into local `main`, clean the feature worktree, and stop at the remote-publication gate.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Stage A evidence is the local commit and local-main integration receipt for this frozen plan.
- Pending Stage B evidence: checker output, test output, local MR review, local-main rollback ref, completed claim, and cleanup record.
<!-- EVIDENCE_INDEX_END -->
