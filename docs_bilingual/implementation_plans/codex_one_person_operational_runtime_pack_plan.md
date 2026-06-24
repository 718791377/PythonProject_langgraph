---
doc_id: codex_one_person_operational_runtime_pack_plan
lang: en
doc_class: implementation_plan
status: final
canonical_path: docs_bilingual/implementation_plans/codex_one_person_operational_runtime_pack_plan.md
zh_cn_path: docs_bilingual/implementation_plans/codex_one_person_operational_runtime_pack_plan.zh-CN.md
---
# Codex And One-Person Company Operational Runtime Pack Plan

## Purpose

Freeze the next implementation wave for the Codex CLI personal production durable-team system embedded inside the personal production one-person-company operating system. This wave does not create another peer white paper and does not regenerate the existing 48/60 body packages. It turns the existing framework into daily fillable, auditable, and reviewable operating artifacts.

## Stage A Boundary

Stage A is this frozen implementation plan plus the document-registry entry only. It must land on local `main` before Stage B starts. Stage A must not create project-kit runtime directories, operating ledgers, checker code, unit tests, CI manifest entries, OpenSpec guard entries, or safety-rule backing entries.

## Stage B Fixed Sequence

Stage B must implement the runtime pack in this exact order:

1. Shared operating ledgers.
2. Codex execution operating pack.
3. One-person-company business operating pack.
4. Mixed dual-gate governance pack.
5. Checker, tests, registry, guard, and safety closeout.

The order matters because shared ledger fields define the audit grammar, Codex and business packs preserve separate truth ownership, mixed governance binds the two gates, and runtime checks fail closed on drift.

## Group 1: Shared Operating Ledgers

Create these bilingual files under `docs_bilingual/project_kits/one_person_company_with_embedded_codex/shared-ledgers/`:

- `README.md` - explains how to use the shared ledger directory.
- `decision-log.md` - records scoped business, Codex, and mixed decisions.
- `risk-register.md` - tracks business, platform, and mixed risks.
- `evidence-register.md` - indexes source evidence and runtime proof.
- `tailoring-decision-log.md` - records full, light, local, module, or hybrid tailoring choices.
- `human-review-records.md` - records human approval for non-delegable decisions.
- `monthly-review.md` - supports monthly operating review and learning.

Each file must have a `.zh-CN.md` companion. Each shared ledger must require these fields: `scope`, `truth_owner`, `evidence_source`, `decision_right`, and `linked_docs`. Shared ledgers may connect business and Codex evidence, but they must not merge business truth with Codex execution truth.

## Group 2: Codex Execution Operating Pack

Create these bilingual files under `docs_bilingual/project_kits/one_person_company_with_embedded_codex/codex-platform/`:

- `agent-routing-policy.md` - defines expert and Agent routing boundaries.
- `worktree-and-branch-protocol.md` - governs isolated worktrees, branches, and local main.
- `openspec-change-lifecycle.md` - governs OpenSpec change flow and archival evidence.
- `durable-state-inspection-and-recovery.md` - defines durable-state inspection and recovery.
- `validation-and-release-gates.md` - defines validation, release, and remote-publication gates.
- `incident-and-rollback-playbook.md` - defines incident response and rollback operations.
- `agent-evaluation-scorecard.md` - evaluates Agent quality, evidence, and failure modes.

These files must state that Codex owns execution truth for Agent routing, OpenSpec, worktree isolation, durable state, local-main evidence, validation gates, rollback, and release-boundary evidence. They must not grant Codex ownership over customers, revenue, pricing, contracts, legal commitments, cashflow, refunds, or customer promises.

## Group 3: One-Person-Company Business Operating Pack

Create these bilingual files under `docs_bilingual/project_kits/one_person_company_with_embedded_codex/business-operations/`:

- `business-operating-cadence.md` - defines daily, weekly, monthly, and quarterly business rhythm.
- `offer-pricing-finance-control.md` - controls offers, pricing, finance, and human approval.
- `customer-intake-and-delivery-workflow.md` - governs customer intake and delivery commitments.
- `sales-support-refund-workflow.md` - governs sales, support, refund, and escalation flow.
- `legal-compliance-contract-control.md` - governs legal, compliance, and contract controls.
- `cashflow-and-runway-review.md` - governs cashflow, runway, and financial review.
- `experiment-to-roadmap-workflow.md` - converts experiments and learning into roadmap choices.

These files must state that the one-person company owns business truth for customers, revenue, pricing, contracts, legal posture, cashflow, support, refunds, delivery commitments, and business learning. They must not let business operating files bypass Agent permissions, runtime validation, durable-state recovery rules, local-main evidence, rollback gates, or remote-publication gates.

## Group 4: Mixed Dual-Gate Governance Pack

Create these bilingual files under `docs_bilingual/project_kits/one_person_company_with_embedded_codex/mixed-governance/`:

- `mixed-change-dual-gate-playbook.md` - defines dual-gate handling for mixed changes.
- `business-to-codex-intake-brief.md` - translates business needs into Codex execution intake.
- `codex-to-business-impact-brief.md` - translates Codex execution changes into business impact.
- `portfolio-roadmap-and-module-tailoring-board.md` - aligns portfolio, roadmap, modules, and tailoring mode.
- `weekly-monthly-quarterly-operating-cadence.md` - coordinates recurring mixed governance cadence.

Each mixed-governance file must require both a business gate and a Codex execution gate when a change affects both customer/revenue/compliance commitments and code/Agent/runtime behavior. The mixed pack must preserve human final approval for pricing, contracts, release, customer promises, financial commitments, legal commitments, and remote publication.

## Process-Group Runtime Grammar

Every execution-facing runtime-pack file must include process-group sections named `Inputs`, `Tools And Techniques`, and `Outputs`. The Chinese companion files must use the equivalent Chinese headings for input, tools-and-techniques, and output. The sections must be practical fillable operating guidance, not only narrative description.

## Stage B Runtime Contract

Stage B must add `tools/check_codex_one_person_operational_runtime_pack.py` and `test/check_codex_one_person_operational_runtime_pack.test.py`. The checker must fail closed when:

- required bilingual files are missing;
- shared ledger fields are missing;
- Codex execution files claim business truth;
- business files claim Agent/runtime release authority;
- mixed-governance files miss the business gate or Codex execution gate;
- process-group sections are missing;
- registry, CI manifest, OpenSpec guard, or safety-rule backing entries are missing.

The checker must expose a `--root` option and a `--json` option. JSON output must include at least `check`, `ok`, `errors`, and `checked_paths`.

## Required Registrations

Stage B must register the runtime pack in:

- `docs_bilingual/docs_registry.yaml` for every new bilingual document and the implementation plan.
- `tools/ci/ci_test_manifest.json` for `check_codex_one_person_operational_runtime_pack.test.py`.
- `tools/run_openspec_guard.py` as guard step `check_codex_one_person_operational_runtime_pack`.
- `tools/safety_rule_script_backing_registry.json` with this plan, the checker, the test, and the guard step.

## Collaboration And Ownership

Stage A is leader-owned because it freezes the plan. After Stage A lands on local `main`, Stage B may use bounded experts or durable-team workers because the runtime pack has independent document and checker slices. Write ownership must remain disjoint: documentation workers own assigned project-kit subdirectories; checker workers own checker and test files; the leader owns registry, guard, safety registration, final fan-in, local validation, and local-main integration.

## Verification Plan

Stage B must run:

```powershell
python .\tools\check_codex_one_person_operational_runtime_pack.py --root . --json
python .\tools\ci\run_python_tests.py --root . --pattern check_codex_one_person_operational_runtime_pack.test.py
python .\tools\check_codex_one_person_next_supplement_sequence.py --root . --json
python .\tools\check_embedded_codex_governance_alignment.py --root . --json
python .\tools\check_operations_package_docs.py --root . --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root .
.\tools\ci\local_gate.ps1 -StepTimeoutSeconds 1800
.\tools\ci\local_mr_review.ps1
```

If the broad local gate needs more time, rerun with a larger `-StepTimeoutSeconds` value before treating it as a regression.

## Local Integration And Publication Boundary

Both stages use the local-main-first workflow. A feature worktree, focused checks, local MR review where applicable, rollback ref, completed claim, and safe cleanup are required before declaring completion. This plan authorizes local `main` integration only. It does not authorize GitLab push, GitLab MR creation or merge, GitHub sync, or any remote publication action.

## Current Status

<!-- CURRENT_STATUS_START -->
- Stage A freezes the operational runtime-pack sequence and registers this plan.
- Stage B is pending until this plan is merged into local `main`.
- Remote publication is not authorized.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Stage A: add this implementation plan and registry entry, validate, commit, merge local `main`, and stop before remote publication.
- Stage B: add shared operating ledgers.
- Stage B: add Codex execution operating pack.
- Stage B: add one-person-company business operating pack.
- Stage B: add mixed dual-gate governance pack.
- Stage B: add checker, test, registry entries, CI manifest entry, OpenSpec guard step, and safety-rule backing entry.
- Stage B: validate, commit, merge local `main`, clean the feature carrier, and stop at the remote-publication gate.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Stage A evidence: plan files, docs registry entry, focused plan-rule check, pre-commit update/archive check, local commit, local-main integration receipt, rollback ref, and completed claim.
- Stage B evidence: runtime-pack checker output, focused unit-test output, dependent governance checker outputs, OpenSpec guard output, local gate, local MR review, local-main integration receipt, rollback ref, completed claim, and cleanup record.
<!-- EVIDENCE_INDEX_END -->
