---
doc_id: operations_package_full_body_generation_plan
doc_class: implementation_plan
status: active
change: expand-operations-package-full-body-doc-generation-20260620
base_ref: main
---

# Operations Package Full Body Generation Plan

> Execution note: this plan is the Stage A frozen brief for Stage B. Stage B must implement this plan from local `main` after this plan package is committed and integrated locally.

## Goal

Expand the governed bilingual operations-package runtime from register/governance package generation into full-body operations document generation for both target systems:

- Codex CLI personal production durable team: 48 English body documents plus 48 zh-CN companions.
- Personal production one-person-company operations: 60 English body documents plus 60 zh-CN companions.

The counts 48 and 60 are acceptance counts for generated body documents. They are not merely inventory numbers inside a register.

## Stage A Package

Stage A freezes this plan, the OpenSpec delta requirements, and the registry entry for this plan. Stage A does not implement the body generator. Stage A must be committed and integrated into local `main` before Stage B begins.

Stage A files:

- `openspec/changes/expand-operations-package-full-body-doc-generation-20260620/` - stores the Stage A OpenSpec proposal, design, tasks, management checklist, and delta specs.
- `docs_bilingual/implementation_plans/operations_package_full_body_generation_plan.md` - freezes the English Stage B implementation brief.
- `docs_bilingual/implementation_plans/operations_package_full_body_generation_plan.zh-CN.md` - freezes the Chinese companion implementation brief.
- `docs_bilingual/docs_registry.yaml` - registers the plan now and the generated body documents in Stage B.

## Stage B Write Scope

Stage B may edit only:

- `tools/generate_operations_package.py` - renders the deterministic operations-package documents.
- `tools/check_operations_package_docs.py` - validates generated package counts, structure, registry, and tailoring rules.
- `test/operations_package_docs.test.py` - provides focused regression coverage for the generator and checker.
- `docs_bilingual/docs_registry.yaml` - registers every generated body-document pair.
- `docs_bilingual/operations_packages/` - stores the generated full-body operations-package documents.

Do not modify LangGraph durable orchestrator source, user-level launcher/routing logic, `.omx/state/`, unrelated governance scripts, unrelated implementation plans, or white papers during Stage B.

## Generated Body Layer

### Codex durable-team package

The generator must create 48 English primary body documents and 48 zh-CN companion documents under:

`docs_bilingual/operations_packages/codex_cli_durable_team/`

The 48 body documents are derived from the tracked Codex core-document list:

1. Strategy and business: `vision.md`, `thesis.md`, `business-model.md`, `pricing.md`, `unit-economics.md`, `strategy.md`.
2. Market and product: `user-segments.md`, `market-map.md`, `research-repository.md`, `product-strategy.md`, `prd.md`, `cli-ux.md`.
3. Metrics and data: `metrics.yaml`, `north-star.md`, `tracking-plan.md`, `data-dictionary.md`, `data-quality-checklist.md`, `experiment-log.md`.
4. Engineering and platform: `architecture.md`, `adr.md`, `module-boundaries.md`, `tech-stack.md`, `delivery-plan.md`, `observability.md`.
5. Security and risk: `security-policy.md`, `access-control.md`, `privacy-policy.md`, `incident-response.md`, `risk-register.md`, `backup-restore.md`.
6. Agent governance: `agent-role-map.md`, `agent-permissions.md`, `agent-tool-policy.md`, `human-review-checklist.md`, `agent-evaluation.md`, `agent-failure-modes.md`.
7. Growth and operations: `growth-model.md`, `docs-plan.md`, `support-playbook.md`, `faq.md`, `trust-page.md`, `changelog.md`.
8. Retrospective and knowledge: `decision-log.md`, `weekly-review.md`, `monthly-review.md`, `postmortem.md`, `learning-log.md`, `template-library.md`.

### One-person-company package

The generator must create 60 English primary body documents and 60 zh-CN companion documents under:

`docs_bilingual/operations_packages/one_person_company/`

The 60 body documents are derived from the tracked one-person-company core-document list:

1. Company strategy: `company-thesis.md`, `vision.md`, `strategy.md`, `annual-plan.md`, `quarterly-plan.md`, `decision-log.md`.
2. Business and finance: `business-model.md`, `offer.md`, `pricing.md`, `unit-economics.md`, `finance-model.md`, `cashflow.md`.
3. Market and user: `market-map.md`, `user-segments.md`, `competitor-analysis.md`, `alternative-solutions.md`, `research-repository.md`, `interview-guide.md`.
4. Product and service: `product-strategy.md`, `prd.md`, `service-blueprint.md`, `onboarding.md`, `customer-journey.md`, `roadmap.md`.
5. Metrics and data: `metrics.yaml`, `north-star.md`, `funnel-dashboard.md`, `tracking-plan.md`, `data-dictionary.md`, `experiment-log.md`.
6. Growth and sales: `growth-model.md`, `channel-map.md`, `sales-playbook.md`, `landing-page.md`, `email-sequences.md`, `content-calendar.md`.
7. Operations and customer success: `ops-playbook.md`, `customer-success-playbook.md`, `support-policy.md`, `faq.md`, `refund-policy.md`, `feedback-triage.md`.
8. Technology and automation: `tech-stack.md`, `automation-map.md`, `tool-stack.md`, `vendor-register.md`, `api-dependency-map.md`, `backup-restore.md`.
9. Governance and risk: `legal-checklist.md`, `terms-of-service.md`, `privacy-policy.md`, `contract-template.md`, `risk-register.md`, `compliance-checklist.md`.
10. Agent and knowledge: `agent-governance.md`, `agent-role-map.md`, `agent-permissions.md`, `human-review-checklist.md`, `monthly-review.md`, `learning-log.md`.

## Per-Document Structure

Every generated body document must include:

1. YAML front matter with `doc_id`, `doc_class`, `status`, `package`, `body_kind`, `generated_by`, and `lang`.
2. Generated marker.
3. Purpose.
4. Authority Boundary.
5. Lifecycle Placement.
6. Tailoring Rules.
7. Inputs.
8. Tools And Techniques.
9. Outputs.
10. Process Group Operating Table.
11. Closeout And Registry.

Chinese companions must include `translation_of` and localized equivalents for the execution sections.

## Process-Group Style

The execution-level flow for every body document uses the process-group grammar:

### Inputs

- Tracked Business Management, product lifecycle, PMP, white-paper, North Star, inventory, and tailoring authorities already committed in the repository.
- The target document family, package, owner, lifecycle layer, risk profile, dependencies, validation needs, rollback or retirement path, and remote-publication boundary.
- Current local worktree state, OpenSpec state, registry state, and package-specific generator selection.

### Tools And Techniques

- 12-layer lifecycle placement, RACI/responsibility-domain mapping, PMI process-group thinking, agile feedback loops, and architecture tailoring scorecard.
- Deterministic generator rendering, registry update, UTF-8-safe writes, checkers, focused tests, local CI, local MR review, and local-main integration helper.
- Expert/durable collaboration only where ownership is disjoint: runtime/checker/test and docs/registry may be separate Stage B slices; leader owns fan-in.

### Outputs

- Generated Markdown body document and zh-CN companion.
- Registry entry with unique doc_id and paths.
- Validation evidence for body counts, bilingual pairing, I/T/O sections, tailoring modes, package isolation, and idempotency.
- Local commit and local `main` integration; remote-publication gate remains closed.

## Tailoring Rules

Every body document must include the five architecture modes:

| Mode | Use when | Lightweight scope |
| --- | --- | --- |
| Full architecture | Cross-stage, external-customer, revenue, compliance, security, publication, rollback, durable-state, shared-runtime, or multi-agent work | Whole affected risk scope is governed end to end |
| Whole-project lightweight | Private, reversible, low-risk exploration with no external commitment, durable-state impact, publication, sensitive data, or shared runtime | The whole project may be lightweight |
| Phase-local lightweight | One discovery, metrics, growth, or retrospective phase is low risk inside a larger governed project | Only that named phase is light |
| Module-level lightweight | One bounded document family, helper, prototype, or local module does not change trust, state, public API, CI, release, or shared runtime behavior | Only that module is light |
| Hybrid architecture | Most real work, where low-risk phases can start light but production, customer, revenue, trust, durable-state, or release impact needs fuller control | Critical layers are full; low-risk phases/modules stay light until escalation triggers fire |

Every tailoring record must state why the selected mode is not heavier or lighter and must list escalation triggers.

## Stage B Tests

Stage B must update tests so they assert:

- Codex body primary count is 48 and body file count is 96.
- One-person-company body primary count is 60 and body file count is 120.
- Every body primary has a zh-CN companion and every companion points to its primary.
- I/T/O sections exist, appear in order, and contain non-empty content.
- All five tailoring modes and escalation trigger language are present.
- Registry has full coverage, unique doc_id values, and unique paths.
- Package-specific write modes do not write the other package.
- Write mode is idempotent and check mode passes after generation.
- English body primaries are ASCII-only; zh-CN companions are strict UTF-8 and contain no replacement character.
- Codex and one-person-company package semantics do not contaminate each other.

## Validation Commands

Stage A:

```powershell
openspec validate expand-operations-package-full-body-doc-generation-20260620 --strict
python .\tools\check_document_pair_policy.py --root . --base-ref main --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root . --tool codex --json
```

Stage B:

```powershell
python .\tools\generate_operations_package.py --root . --package all --check --json
python .\tools\generate_operations_package.py --root . --package codex --check --json
python .\tools\generate_operations_package.py --root . --package one-person-company --check --json
python .\tools\check_operations_package_docs.py --root . --json
python .\tools\ci\run_python_tests.py --root . --pattern operations_package_docs.test.py
openspec validate expand-operations-package-full-body-doc-generation-20260620 --strict
openspec validate --all --strict
python .\tools\run_openspec_guard.py --root . --tool codex --json
```

Before each commit, run the pre-commit update/archive checker. Before local-main integration, run the repository local gate and local MR review, or use the guarded local integration helper that runs them.

## Collaboration And Durable-Team Rule

Stage A is leader-owned because the frozen plan does not yet exist on local `main`. Advisory experts may review the plan.

Stage B has at least two mostly independent slices after Stage A lands:

1. Runtime/checker/test slice.
2. Generated docs/registry slice.

When the backend preflight is ready and ownership can remain disjoint, Stage B should adopt the smallest sufficient durable or expert execution surface. If durable team tooling is blocked, use bounded native experts and keep the leader responsible for final integration and validation.

## Completion Boundary

Completion requires both local-main integrations:

1. Stage A plan-freeze commit integrated into local `main`.
2. Stage B runtime/body-doc commit integrated into local `main`.

The work stops at the remote-publication gate unless the user explicitly authorizes remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
- Stage A artifacts have been drafted in the feature worktree and are pending validation, commit, and local `main` integration.
- Stage B must not start until the Stage A plan-freeze package is integrated into local `main`.
- Remote publication is not authorized.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Stage A: validate OpenSpec, bilingual pair policy, pre-commit update/archive policy, and repository OpenSpec guard.
- Stage A: commit the plan-freeze package and integrate it into local `main`.
- Stage B: implement the full-body runtime, generate the 48/60 body layer, validate, commit, and integrate it into local `main`.
- Closeout: archive the OpenSpec change after Stage B validation and stable-spec sync.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- `openspec/changes/expand-operations-package-full-body-doc-generation-20260620/` - Stage A OpenSpec proposal, design, tasks, management, and delta specs.
- `docs_bilingual/implementation_plans/operations_package_full_body_generation_plan.md` - frozen English implementation plan.
- `docs_bilingual/implementation_plans/operations_package_full_body_generation_plan.zh-CN.md` - frozen Chinese companion implementation plan.
- `docs_bilingual/docs_registry.yaml` - registry entry for the implementation plan and Stage B body-document registry target.
<!-- EVIDENCE_INDEX_END -->
