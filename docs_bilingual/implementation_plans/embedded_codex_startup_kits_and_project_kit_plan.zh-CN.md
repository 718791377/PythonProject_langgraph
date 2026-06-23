---
doc_id: embedded_codex_startup_kits_and_project_kit_plan
doc_class: implementation_plan
status: final
canonical_path: docs_bilingual/implementation_plans/embedded_codex_startup_kits_and_project_kit_plan.md
zh_cn_path: docs_bilingual/implementation_plans/embedded_codex_startup_kits_and_project_kit_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/embedded_codex_startup_kits_and_project_kit_plan.md
---
# Embedded Codex Startup Kits And Project Kit Plan - zh-CN Companion

## Purpose

This zh-CN companion freezes the same implementation contract as the English primary. Stage B turns the existing 48 Codex durable-team body documents and 60 one-person-company body documents into startup-ready, reusable, auditable operating kits. The one-person company owns business truth, and the embedded Codex durable team owns execution truth.

## Stage A Boundary

Stage A is this frozen implementation plan plus registry registration only. It is a docs-only governance confirmation package. It must land on local main before Stage B starts. Stage A does not create templates, project-kit files, runtime checkers, tests, or generated package changes.

## Stage B Output Set

Stage B must add bilingual document groups for the Codex minimum startup list, the one-person-company embedded Codex startup matrix, shared governance ledger templates, a tailoring decision record template, and the one-person-company with embedded Codex project kit. Stage B must register every new bilingual pair in docs_bilingual/docs_registry.yaml.

## Stage B Runtime Contract

Stage B must add tools/check_embedded_codex_startup_kits.py and test/check_embedded_codex_startup_kits.test.py. The checker must fail closed when required files, registry entries, shared ledger fields, tailoring fields, project-kit files, process-group sections, CI manifest registration, guard registration, or safety-rule registry registration are missing.

## Required Codex Minimum Startup Order

1. thesis.md
2. architecture.md
3. agent-governance.md
4. agent-role-map.md
5. agent-permissions.md
6. delivery-plan.md
7. observability.md
8. risk-register.md
9. human-review-checklist.md
10. decision-log.md
11. backup-restore.md
12. monthly-review.md

This list is the minimum embedded platform-governance start set for agents, worktrees, durable state, validation gates, release gates, evidence, rollback, and review. It is not a business-startup list.

## Required Startup Matrix Contract

The matrix must map one-person-company startup documents, embedded Codex startup documents, shared ledgers, scope, truth_owner, evidence_source, decision_right, two-gate triggers, and escalation notes. Mixed customer, revenue, or compliance work plus code, Agent, or runtime work requires both the business gate and the Codex execution gate.

## Process Group Style

Execution-facing new files must include process-group language. Files that prescribe operating behavior must include Inputs, Tools And Techniques, and Outputs. Chinese-facing wording should use the equivalent concepts: input, tools and techniques, and output.

## Verification Plan

Stage B must run the focused startup-kit checker, its unit test, the embedded-governance alignment checker, the operations-package checker, and the pre-commit update/archive checker. Before Stage B local-main integration, run local MR review and the broad local gate when it is not blocked by a pre-existing unrelated external plugin or cache issue.

## Local Integration And Publication Boundary

Stage A and Stage B use local-main-first integration. A clean feature worktree, focused validation, local MR review, rollback ref, and completed claim are required before declaring completion. This plan does not authorize GitLab or GitHub remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
- Stage A freezes the startup kits and project-kit implementation contract.
- Stage B is pending until this plan is merged into local main and the current user implementation request is recorded as the implementation confirmation.
- Durable-team threshold is re-evaluated for Stage B because Stage B has independent docs/template and checker/test slices; native expert assistance may be used with leader-owned fan-in.
- Remote publication is not authorized.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Completed in Stage A: freeze this implementation plan and register it.
- Pending for Stage B: create the Codex minimum startup list and embedded startup matrix.
- Pending for Stage B: create shared ledger templates, tailoring record template, and project kit files.
- Pending for Stage B: add checker, tests, guard registration, CI manifest registration, safety-rule registry entry, and docs registry entries.
- Pending for Stage B: validate, commit, integrate into local main, clean the feature worktree, and stop at the remote-publication gate.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Stage A evidence is the local commit and local-main integration receipt for this frozen plan.
- Pending Stage B evidence: checker output, test output, local MR review, local-main rollback ref, completed claim, and cleanup record.
<!-- EVIDENCE_INDEX_END -->
