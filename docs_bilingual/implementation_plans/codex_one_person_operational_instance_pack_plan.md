---
doc_id: codex_one_person_operational_instance_pack_plan
lang: en
doc_class: implementation_plan
status: active
canonical_path: docs_bilingual/implementation_plans/codex_one_person_operational_instance_pack_plan.md
zh_cn_path: docs_bilingual/implementation_plans/codex_one_person_operational_instance_pack_plan.zh-CN.md
---
# Codex And One-Person Company Operational Instance Pack Plan

## Purpose

Freeze the next implementation wave for the Codex CLI personal production durable-team system embedded inside the personal production one-person-company operating system. This wave adds fillable operational instance records so the existing white papers, North Stars, lifecycle skeletons, 48/60 operations packages, project kit, and operational runtime pack can be used and audited in daily, weekly, monthly, and quarterly operations.

This plan does not create a third peer white paper. It does not regenerate the existing 48/60 body packages. It adds a project-kit instance layer for real run records while preserving the rule that Codex is embedded platform governance and the one-person company owns business truth.

## Stage A Boundary

Stage A is this frozen implementation plan plus the document-registry entry only. It must land on local `main` before Stage B starts. Stage A must not create `operational-instances/`, instance records, checker code, unit tests, CI manifest entries, OpenSpec guard entries, or safety-rule backing entries.

## Stage B Fixed Sequence

Stage B must implement the operational instance pack in this exact order:

1. Instance entrypoint.
2. Shared ledger instances.
3. Codex execution instances.
4. One-person-company business instances.
5. Mixed dual-gate instances.
6. Checker, tests, registry, guard, and safety closeout.

The fixed implementation order is: entrypoint -> shared ledgers -> Codex execution -> business operations -> mixed dual gates -> checker closeout.

## Group 1: Instance Entrypoint

Create these bilingual files under `docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/`:

- `README.md` - explains how to use the instance directory.
- `instance-profile.md` - defines the real project, product, customer cycle, or release slice represented by the instance.
- `operating-calendar.md` - defines daily, weekly, monthly, and quarterly operating cadence for the instance.
- `artifact-index.md` - indexes evidence, source documents, ledgers, runtime records, and review outputs.

Each file must have a `.zh-CN.md` companion. These files define the boundary, cadence, evidence entrypoint, and artifact index for one real operational instance.

## Group 2: Shared Ledger Instances

Create these bilingual files under `docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/shared-ledgers/`:

- `decision-log.instance.md` - records actual scoped decisions.
- `risk-register.instance.md` - records actual business, Codex, and mixed risks.
- `evidence-register.instance.md` - records actual customer, revenue, repo, runtime, agent, and legal evidence.
- `tailoring-decision-log.instance.md` - records actual full, whole-project lightweight, phase-local lightweight, module-level lightweight, or hybrid tailoring decisions.
- `human-review-records.instance.md` - records actual human approvals and non-delegable decisions.
- `monthly-review.instance.md` - records actual monthly operating review and learning.

Each shared ledger instance must require `scope`, `truth_owner`, `evidence_source`, `decision_right`, and `linked_docs`. Shared ledgers may connect business, Codex, and mixed evidence, but business, codex, and mixed facts must remain scoped and must not be merged into one truth owner.

## Group 3: Codex Execution Instances

Create these bilingual files under `docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/codex-platform/`:

- `runtime-run-record.md` - records an actual Agent or runtime execution.
- `local-main-integration-record.md` - records local main integration evidence.
- `validation-release-readiness-record.md` - records validation, release readiness, and remote-publication gate state.
- `agent-evaluation-run-record.md` - records actual Agent evaluation results.
- `durable-state-recovery-drill.md` - records a durable-state inspection or recovery drill.
- `incident-rollback-case-record.md` - records a Codex incident and rollback case.

These files must state that Codex owns execution truth for Agent routing, OpenSpec, worktree isolation, durable state, validation gates, local-main evidence, rollback, and release-boundary evidence. They must not grant Codex ownership over customers, revenue, pricing, contracts, legal commitments, cashflow, refunds, or customer promises.

## Group 4: One-Person-Company Business Instances

Create these bilingual files under `docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/business-operations/`:

- `offer-pricing-decision-record.md` - records actual offer and pricing decisions.
- `customer-intake-delivery-record.md` - records actual customer intake and delivery commitments.
- `sales-support-refund-case-record.md` - records actual sales, support, refund, and escalation cases.
- `legal-contract-review-record.md` - records actual legal and contract review.
- `cashflow-runway-review-record.md` - records actual cashflow and runway review.
- `experiment-roadmap-readout.md` - records actual experiment learning and roadmap decisions.

These files must state that the one-person company owns business truth for customers, revenue, pricing, contracts, legal posture, cashflow, support, refunds, delivery commitments, and business learning. They must not let business operating files bypass Agent permissions, runtime validation, durable-state recovery rules, local-main evidence, rollback gates, or remote-publication gates.

## Group 5: Mixed Dual-Gate Instances

Create these bilingual files under `docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/mixed-governance/`:

- `mixed-change-record.md` - records a real mixed business and Codex change.
- `business-to-codex-intake-instance.md` - records a real business-to-Codex intake.
- `codex-to-business-impact-instance.md` - records a real Codex-to-business impact brief.
- `module-tailoring-decision-record.md` - records an actual module tailoring decision.
- `dual-gate-release-record.md` - records an actual release that requires both gates.
- `quarterly-portfolio-review-record.md` - records quarterly portfolio review across business and Codex operations.

Each mixed-governance instance must require both a business gate and a Codex execution gate when a change affects both customer, revenue, or compliance commitments and code, Agent, or runtime behavior. The mixed pack must preserve human final approval for pricing, contracts, release, customer promises, financial commitments, legal commitments, and remote publication.

## Process-Group Runtime Grammar

Every execution-facing instance file must include process-group sections named `Inputs`, `Tools And Techniques`, and `Outputs`. The Chinese companion files must use the standard Chinese process-group headings for input, tools-and-techniques, and output. The sections must be practical fillable operating records, not only narrative description.

## Stage B Runtime Contract

Stage B must add `tools/check_codex_one_person_operational_instance_pack.py` and `test/check_codex_one_person_operational_instance_pack.test.py`. The checker must fail closed when:

- required bilingual files are missing;
- required registry entries are missing;
- shared ledger fields are missing;
- Codex execution instances claim business truth;
- business instances claim Agent or runtime release authority;
- mixed-governance instances miss the business gate, Codex execution gate, or human final approval;
- process-group sections are missing or Chinese files fall back to English headings;
- CI manifest, OpenSpec guard, guard JSON test, or safety-rule backing entries are missing.

The checker must expose a `--root` option and a `--json` option. JSON output must include at least `check`, `ok`, `errors`, `warnings`, `groups`, and `checked_paths`.

## Required Registrations

Stage B must register the instance pack in:

- `docs_bilingual/docs_registry.yaml` for every new bilingual document and this implementation plan.
- `tools/ci/ci_test_manifest.json` for `check_codex_one_person_operational_instance_pack.test.py`.
- `tools/run_openspec_guard.py` as guard step `check_codex_one_person_operational_instance_pack`.
- `test/run_openspec_guard_json.test.py` for the new guard step.
- `tools/safety_rule_script_backing_registry.json` with this plan, the checker, the test, and the guard step.

## Collaboration And Ownership

Stage A is leader-owned because it freezes the plan. After Stage A lands on local `main`, Stage B may use bounded experts or a durable team because the instance pack has independent documentation, checker, and verification slices. Write ownership must remain disjoint: documentation workers own assigned project-kit subdirectories; checker workers own checker and test files; the leader owns registry, guard, safety registration, final fan-in, local validation, and local-main integration.

## Verification Plan

Stage B must run:

```powershell
python .	ools\check_codex_one_person_operational_instance_pack.py --root . --json
python .	ools\ci
un_python_tests.py --root . --pattern check_codex_one_person_operational_instance_pack.test.py
python .	ools\check_codex_one_person_operational_runtime_pack.py --root . --json
python .	ools\check_codex_one_person_next_supplement_sequence.py --root . --json
python .	ools\check_embedded_codex_governance_alignment.py --root . --json
python .	ools\check_operations_package_docs.py --root . --json
python .	ools\check_precommit_update_archive.py --root . --json
python .	ools
un_openspec_guard.py --root . --json
.	ools\ci\local_gate.ps1 -StepTimeoutSeconds 1800
.	ools\ci\local_mr_review.ps1
```

If the broad local gate needs more time, rerun with a larger `-StepTimeoutSeconds` value before treating it as a regression.

## Local Integration And Publication Boundary

Both stages use the local-main-first workflow. A feature worktree, focused checks, local MR review where applicable, rollback ref, completed claim, and safe cleanup are required before declaring completion. This plan authorizes local `main` integration only. It does not authorize GitLab push, GitLab MR creation or merge, GitHub sync, or any remote publication action.

## Current Status

<!-- CURRENT_STATUS_START -->
- Stage A froze the operational instance-pack sequence and registered this plan on local `main` in commit `a542bde`.
- Stage B implemented the operational instance pack, checker, tests, registry, guard, and safety backing on local `main` in commit `7239ced`.
- Post-merge validation passed on local `main`: instance-pack checker, focused unit test, OpenSpec guard, local gate, and local MR review evidence are recorded in the completed claim.
- Remote publication is not authorized and has not been performed.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Completed: Stage A added this implementation plan and registry entry, validated it, merged local `main`, and stopped before remote publication.
- Completed: Stage B added instance entrypoint documents.
- Completed: Stage B added shared ledger instance records.
- Completed: Stage B added Codex execution instance records.
- Completed: Stage B added one-person-company business instance records.
- Completed: Stage B added mixed dual-gate instance records.
- Completed: Stage B added checker, test, registry entries, CI manifest entry, OpenSpec guard step, guard JSON test entry, and safety-rule backing entry.
- Completed: Stage B validated, committed, merged local `main`, cleaned the feature carrier, and stopped at the remote-publication gate.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Stage A evidence: plan files, docs registry entry, focused plan-rule check, pre-commit update/archive check, local commit `a542bde`, local-main integration receipt, rollback ref, and completed claim `freeze-codex-one-person-operational-instance-pack-20260625.json`.
- Stage B evidence: operational instance files under `docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/`, checker `tools/check_codex_one_person_operational_instance_pack.py`, focused unit test `test/check_codex_one_person_operational_instance_pack.test.py`, guard/CI/safety registrations, OpenSpec guard output, local gate, local MR review, local commit `7239ced`, rollback ref `refs/backup/local-main/20260626-091013-before-implement-codex-one-person-operational-instance-pack-20260626`, completed claim `implement-codex-one-person-operational-instance-pack-20260626.json`, and cleanup record.
<!-- EVIDENCE_INDEX_END -->
