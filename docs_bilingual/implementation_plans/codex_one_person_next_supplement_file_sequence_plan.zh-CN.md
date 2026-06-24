---
doc_id: codex_one_person_next_supplement_file_sequence_plan
lang: zh-CN
doc_class: implementation_plan
status: final
canonical_path: docs_bilingual/implementation_plans/codex_one_person_next_supplement_file_sequence_plan.md
zh_cn_path: docs_bilingual/implementation_plans/codex_one_person_next_supplement_file_sequence_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/codex_one_person_next_supplement_file_sequence_plan.md
---
# Codex And One-Person Company Next Supplement File Sequence Plan - zh-CN Companion

## Purpose

This zh-CN companion freezes the same implementation contract as the English primary. It is kept ASCII-safe so Windows launcher, PowerShell, and repository mojibake guards can validate it reliably. Stage B may expand Chinese prose through a UTF-8-safe writer, but this Stage A companion already carries the complete governance contract.

## Stage A Boundary

Stage A is this frozen implementation plan plus registry registration only. It is a documentation-only governance confirmation package. It must land on local main before Stage B starts. Stage A does not change lifecycle files, operations packages, project kit pages, templates, runtime checkers, tests, guard registration, or generated package contents.

## Stage B Output Sequence

Stage B must update and validate the following five ordered groups:

1. Shared boundary and tailoring rules.
2. Codex-side governance skeleton.
3. One-person-company-side governance skeleton.
4. Two white papers and two North Star documents.
5. Project kit and operations-package closeout.

The fixed order is: shared -> Codex -> one-person company -> white papers and North Stars -> project kit and body packages.

## Required Group 1: Shared Boundary And Tailoring Rules

Stage B updates these bilingual files first:

- `docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.md` - defines tailoring scope and escalation rules.
- `docs_bilingual/product_lifecycle/ten_to_twelve_layer_bridge.md` - maps runtime capability layers into lifecycle layers.
- `docs_bilingual/product_lifecycle/durable_team_process_group_contract.md` - defines process-group I/T/O execution grammar.
- `docs_bilingual/product_lifecycle/durable_team_source_traceability.md` - records source-to-document traceability boundaries.
- `docs_bilingual/product_lifecycle/fresh_source_reading_evidence.md` - indexes fresh source-reading evidence.

The update must clarify full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, and hybrid tailoring. Tailoring does not delete the twelve-layer mental model; lightweight scope must be explicit.

## Required Group 2: Codex-Side Governance Skeleton

Stage B then updates:

- `docs_bilingual/product_lifecycle/codex_platform_inventory_map.md` - anchors the Codex platform target inventory.
- `docs_bilingual/product_lifecycle/codex_platform_virtual_departments_operating_map.md` - maps Codex virtual departments.
- `docs_bilingual/product_lifecycle/codex_platform_responsibility_raci.md` - defines Codex responsibility ownership.
- `docs_bilingual/product_lifecycle/codex_platform_core_documents_register.md` - registers Codex core documents.
- `docs_bilingual/product_lifecycle/codex_platform_cross_cutting_module_map.md` - maps Codex cross-cutting modules.
- `docs_bilingual/product_lifecycle/codex_platform_governed_agent_catalog.md` - catalogs governed Codex agents.
- `docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_document_generation_order.md` - defines Codex package generation order.
- `docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_operating_slice_template.md` - templates Codex operating slices.
- `docs_bilingual/product_lifecycle/codex_durable_team_platform_build_lifecycle.md` - defines Codex platform build lifecycle.

These files must keep Codex as the execution-truth owner for agents, worktrees, OpenSpec, durable state, validation gates, local-main evidence, rollback, and release boundaries.

## Required Group 3: One-Person-Company Governance Skeleton

Stage B then updates:

- `docs_bilingual/product_lifecycle/one_person_company_inventory_map.md` - anchors one-person-company target inventory.
- `docs_bilingual/product_lifecycle/one_person_company_minimum_startup_documents.md` - defines one-person-company startup set.
- `docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.md` - maps embedded Codex startup boundaries.
- `docs_bilingual/product_lifecycle/one_person_company_tailoring_decision_tree.md` - guides one-person-company tailoring decisions.
- `docs_bilingual/product_lifecycle/one_person_company_architecture_mode_selection_guide.md` - selects full, light, or hybrid architecture modes.
- `docs_bilingual/product_lifecycle/one_person_company_pmi_process_group_playbook.md` - applies PMI process-group operating grammar.
- `docs_bilingual/product_lifecycle/one_person_company_operations_document_system.md` - defines one-person-company document system.
- `docs_bilingual/product_lifecycle/one_person_company_operations_metrics_and_monthly_review.md` - connects metrics and review cadence.
- `docs_bilingual/product_lifecycle/codex_project_consumption_lifecycle.md` - defines downstream project consumption lifecycle.

These files must keep the one-person company as the business-truth owner for customers, revenue, pricing, contracts, legal posture, cashflow, support, delivery commitments, and business learning. Embedded Codex remains a platform-governance capability, not a peer business authority.

## Required Group 4: White Papers And North Stars

Stage B then updates:

- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md` - summarizes Codex platform narrative.
- `docs_bilingual/north_star/codex_cli_personal_production_durable_team_north_star.md` - aliases the Codex North Star authority.
- `docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.md` - summarizes one-person-company narrative.
- `docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md` - defines one-person-company operating-loop metric.

The closeout language must preserve the 10-layer runtime capability versus 12-layer lifecycle bridge and explicitly prevent Codex platform truth from redefining business truth.

## Required Group 5: Project Kit And Body Package Closeout

Stage B finally updates:

- `docs_bilingual/project_kits/one_person_company_with_embedded_codex/*` - closes the embedded project kit guidance.
- `docs_bilingual/operations_packages/codex_cli_durable_team/*` - closes Codex body-package references.
- `docs_bilingual/operations_packages/one_person_company/*` - closes one-person-company body-package references.

This group closes references and operating guidance. It must not create a third peer white paper and must not regenerate unrelated body-package content for its own sake.

## Process Group Requirement

Execution-facing files must include process-group wording with `Inputs`, `Tools And Techniques`, and `Outputs`. Chinese companion files must use equivalent input, tools-and-techniques, and output concepts. The Stage B checker must verify these surfaces.

## Stage B Runtime Contract

Stage B must add:

- `tools/check_codex_one_person_next_supplement_sequence.py` - validates the supplement sequence contract.
- `test/check_codex_one_person_next_supplement_sequence.test.py` - tests the supplement sequence checker.

The checker must fail closed when ordered groups, bilingual pairs, registry entries, truth-boundary language, tailoring-scope language, process-group sections, CI registration, guard registration, or safety registration are missing.

## Collaboration And Ownership

Stage A is leader-owned. Stage B may use bounded experts or durable-team workers after this plan is merged to local main. Workers may update assigned lifecycle or package documents. The leader owns registry, checker, tests, CI manifest, OpenSpec guard, safety registry, final fan-in, and local-main integration.

## Verification Plan

Stage B must run the focused checker, its unit test, embedded-governance checker, startup-kit checker, operations-package checker, pre-commit update/archive checker, local gate, and local MR review. If the broad local gate hits a default timeout, rerun with a larger StepTimeoutSeconds value before treating it as a regression.

## Local Integration And Publication Boundary

Stage A and Stage B use local-main-first integration. A clean feature worktree, focused validation, local MR review, rollback ref, completed claim, and safe cleanup are required before declaring completion. This plan does not authorize GitLab or GitHub remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
- Stage A freezes the next supplement file sequence and registers this plan.
- Stage B is pending until this plan is merged into local main and the current user implementation request is recorded as implementation confirmation.
- Remote publication is not authorized.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Stage A: add this implementation plan and registry entry, validate, commit, merge local main, and stop before remote publication.
- Stage B: update shared boundary and tailoring files.
- Stage B: update Codex-side governance skeleton files.
- Stage B: update one-person-company-side governance skeleton files.
- Stage B: update white papers, North Stars, project kit, and operations-package closeout references.
- Stage B: add checker, tests, CI manifest registration, OpenSpec guard registration, and safety-rule registry entry.
- Stage B: validate, commit, merge local main, clean the feature carrier, and stop at the remote-publication gate.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Stage A evidence: local commit, local-main integration receipt, rollback ref, and completed claim for this frozen plan.
- Pending Stage B evidence: checker output, test output, embedded-governance checker output, startup-kit checker output, operations-package checker output, local gate, local MR review, rollback ref, completed claim, and cleanup record.
<!-- EVIDENCE_INDEX_END -->
