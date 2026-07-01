---
doc_id: embedded_codex_governance_alignment_runtime_plan
doc_class: implementation_plan
status: final
canonical_path: docs_bilingual/implementation_plans/embedded_codex_governance_alignment_runtime_plan.md
zh_cn_path: docs_bilingual/implementation_plans/embedded_codex_governance_alignment_runtime_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/embedded_codex_governance_alignment_runtime_plan.md
---
# Embedded Codex Governance Alignment Runtime Plan - zh-CN Companion

## Purpose

This zh-CN companion mirrors and freezes the runtime validation contract for the one-person-company embedded Codex governance relationship. It follows the already integrated forced naming plan, but adds a hard live checker so future edits cannot make the Codex CLI personal production durable team compete with the one-person-company operating system for business truth.

The frozen rule is: the one-person company owns business truth, the embedded Codex durable team owns execution truth, mixed matters require both gates, and AI agents never own final commitment rights.

## Scope

The runtime checker must inspect these repository surfaces:

- `docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.md` - English policy source for embedded-governance truth boundaries.
- `docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.zh-CN.md` - zh-CN policy companion for the same boundary.
- `docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.md` - one-person-company white paper that must link the embedded boundary.
- `docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md` - North Star surface that must require both gates for mixed loops.
- `docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.md` - prior forced-rename plan consumed by this runtime plan.
- `docs_bilingual/implementation_plans/embedded_codex_governance_alignment_runtime_plan.md` - this frozen runtime checker contract.
- `docs_bilingual/docs_registry.yaml` - registry authority for bilingual docs and generated package paths.
- `docs_bilingual/operations_packages/codex_cli_durable_team/` - separated Codex execution-truth package directory.
- `docs_bilingual/operations_packages/one_person_company/` - separated business-truth package directory.
- `tools/generate_operations_package.py` - generator inventory and expected generated-file source.
- `tools/check_operations_package_docs.py` - existing generated package and stale-name guard.

## Frozen Governance Contract

### Inputs

- User-approved embedded governance wording.
- Existing generated 48 Codex durable-team body documents and 60 one-person-company body documents.
- Existing bilingual governance policy and forced-rename implementation plan.
- Existing registry, generator, and operations-package checker.

### Tools And Techniques

- Bilingual implementation-plan registration through `docs_bilingual/docs_registry.yaml`.
- Runtime checker with fail-closed JSON output.
- OpenSpec guard registration.
- CI manifest registration for the checker regression test.
- Local-main-first integration with rollback ref and completed claim.

### Outputs

- A frozen runtime checker contract in this plan.
- `tools/check_embedded_codex_governance_alignment.py` in Stage B.
- `test/check_embedded_codex_governance_alignment.test.py` in Stage B.
- OpenSpec guard and local CI coverage in Stage B.

## Canonical Name Contract

The runtime checker must treat these filenames as canonical physical files:

| Semantic slot | Canonical physical name | Legacy alias that must not reappear as a generated physical file |
| --- | --- | --- |
| Agent governance | `agent-governance.md` | `agent-tool-policy.md` |
| Existence thesis | `thesis.md` | `company-thesis.md` |
| Metrics | `metrics.md` | `metrics.yaml` |
| Support operations | `support-playbook.md` | `support-policy.md` |

The checker must fail if legacy physical files or registry paths reappear in either generated operations-package directory or `docs_bilingual/docs_registry.yaml`.

## Shared Ledger Contract

The checker must confirm that shared ledgers are documented and require every record to carry:

```yaml
scope: business | codex | mixed
truth_owner: founder | codex-operator | human-review
evidence_source: customer | revenue | repo | runtime | agent | legal
decision_right: human | delegated-draft-only
linked_docs: []
```

Required shared ledgers:

- `decision-log.md` - shared decision ledger with business, codex, or mixed scope.
- `risk-register.md` - shared risk ledger split by business, platform, and mixed risks.
- `learning-log.md` - shared learning ledger for customer, operations, and platform learning.
- `experiment-log.md` - shared experiment ledger for market, product, and automation tests.
- `data-dictionary.md` - shared dictionary separating business data, telemetry, and agent state.
- `tracking-plan.md` - shared event plan separating business and platform events.
- `backup-restore.md` - shared recovery manual with business data, repo, and durable-state sections.
- `agent-role-map.md` - shared role map distinguishing business agents and Codex execution agents.
- `agent-permissions.md` - shared permission matrix split by tool, data, and approval right.
- `human-review-checklist.md` - shared human-review checklist for commitments and execution gates.
- `monthly-review.md` - shared monthly review for business-loop and platform-execution quality.

## Same Name Separate Truth Contract

The checker must confirm that same-name documents are allowed only as package-specific truth in separate directories:

- `vision.md` - same-name vision slot with package-specific truth.
- `strategy.md` - same-name strategy slot with business or platform meaning by package.
- `business-model.md` - same-name model slot split between revenue model and productivity model.
- `pricing.md` - same-name pricing slot split between customer pricing and platform-cost assumptions.
- `unit-economics.md` - same-name economics slot split between customer and automation economics.
- `user-segments.md` - same-name segment slot split between customers and developer/project types.
- `market-map.md` - same-name market-map slot split between business market and platform alternatives.
- `north-star.md` - same-name North Star slot split between business throughput and delivery reliability.
- `metrics.md` - same-name metrics slot split between business and execution metrics.
- `prd.md` - same-name PRD slot split between customer product and platform capability.
- `tech-stack.md` - same-name technology slot split between runtime dependencies and Codex tooling.
- `privacy-policy.md` - same-name privacy slot split between customer promises and tool-state handling.

These names may exist in both `codex_cli_durable_team/` and `one_person_company/`, but content and front matter must still identify the package-specific owner.

## Separate Truth Boundary Contract

Business-only files must stay out of the Codex generated package:

- `offer.md` - business-only offer and customer promise document.
- `finance-model.md` - business-only finance, runway, and viability document.
- `cashflow.md` - business-only cash timing and survival document.
- `contract-template.md` - business-only customer or partner contract document.
- `terms-of-service.md` - business-only customer-facing service terms document.
- `sales-playbook.md` - business-only sales motion and commitment-control document.
- `customer-success-playbook.md` - business-only customer-success operating document.
- `refund-policy.md` - business-only refund and remedy policy document.
- `legal-checklist.md` - business-only legal review trigger document.
- `compliance-checklist.md` - business-only regulatory and compliance trigger document.

Codex-only files must stay out of the one-person-company generated package:

- `architecture.md` - Codex-only platform architecture document.
- `adr.md` - Codex-only architecture decision record document.
- `module-boundaries.md` - Codex-only code, tool, and integration boundary document.
- `observability.md` - Codex-only runtime telemetry and reliability document.
- `agent-evaluation.md` - Codex-only agent quality and acceptance-evidence document.
- `agent-failure-modes.md` - Codex-only agent failure taxonomy and mitigation document.
- `access-control.md` - Codex-only platform access and operation-rights document.
- `incident-response.md` - Codex-only platform incident response document.
- `delivery-plan.md` - Codex-only code delivery, validation, and release-boundary document.

`agent-governance.md` is allowed in both packages only because it is a shared semantic slot with package-specific truth. The checker must distinguish that exception from Codex-only files.

## Semantic Mapping Contract

The checker must confirm that the governance policy documents the following semantic bridges:

| Codex document | One-person-company document |
| --- | --- |
| `thesis.md` | `thesis.md` |
| `agent-governance.md` | `agent-governance.md` |
| `agent-evaluation.md` | `agent-governance.md` / `human-review-checklist.md` |
| `agent-failure-modes.md` | `risk-register.md` |
| `architecture.md` | `automation-map.md` |
| `adr.md` | `decision-log.md` |
| `module-boundaries.md` | `tool-stack.md` / `api-dependency-map.md` |
| `delivery-plan.md` | `roadmap.md` / `quarterly-plan.md` |
| `observability.md` | `funnel-dashboard.md` / `metrics.md` |
| `security-policy.md` | `legal-checklist.md` / `compliance-checklist.md` |
| `access-control.md` | `agent-permissions.md` |
| `incident-response.md` | `support-playbook.md` / `feedback-triage.md` |
| `support-playbook.md` | `customer-success-playbook.md` / `support-playbook.md` |
| `cli-ux.md` | `onboarding.md` / `service-blueprint.md` |
| `changelog.md` | `roadmap.md` / `monthly-review.md` |
| `postmortem.md` | `learning-log.md` |
| `template-library.md` | `content-calendar.md` / `landing-page.md` |

## Runtime Checker Requirements

Stage B must add `tools/check_embedded_codex_governance_alignment.py` with this CLI:

```powershell
python .\tools\check_embedded_codex_governance_alignment.py --root . --json
```

The checker must emit:

- `schema_version` - JSON schema version for checker output.
- `generated_at` - timestamp for checker output.
- `check_name` - stable checker identifier.
- `ok` - boolean pass or fail result.
- `root` - resolved repository root inspected by the checker.
- `errors` - fail-closed findings that must block the gate.
- `warnings` - non-blocking advisory findings.
- `info` - informational evidence strings.
- `counts` - summary counts for checked surfaces and findings.

It must fail when:

- required governance or plan documents are missing;
- embedded capability, business truth, execution truth, two gates, human final commitment rights, or shared ledger fields are missing;
- canonical package files are missing;
- legacy physical files or legacy registry paths reappear;
- `docs_bilingual/docs_registry.yaml` has duplicate `doc_id`, duplicate canonical or zh path, missing bilingual companions, or points to legacy doc IDs or paths;
- generated package counts drift from 48 Codex primaries, 60 one-person-company primaries, 96 Codex files, 120 one-person-company files, and 216 total generated files;
- business-only files appear under the Codex package;
- Codex-only files appear under the one-person-company package;
- semantic mapping entries are missing;
- the runtime plan, governance policy, white paper, North Star, or registry stop linking the embedded governance boundary.

Stage B must also keep Chinese UTF-8 readability intact: the checker must not bless mojibake, Unicode replacement characters, or corrupted Chinese snippets as canonical evidence.

## OpenSpec And Local Integration Boundary

- Stage A freezes this runtime plan only; if Stage B produces a completed active OpenSpec change, that change must be archived before commit or carry an explicit archive deferral marker and follow-up.
- Stage A and Stage B use local-main-first integration; passing local gates and local MR review permits automatic integration into local `main`.
- This plan does not authorize GitLab or GitHub push, MR creation, MR update, MR merge, mirror sync, or any remote ref mutation.

## CI And Guard Registration

Stage B must register:

- `test/check_embedded_codex_governance_alignment.test.py` in `tools/ci/ci_test_manifest.json`.
- `tools/check_embedded_codex_governance_alignment.py` in `tools/run_openspec_guard.py` near document and operations-package checks.

The new test must include positive coverage for the current repository and negative coverage for missing governance anchors, missing shared ledger fields, legacy physical files, missing canonical files, wrong package placement, missing registry anchors, and missing CI manifest registration.

## Stage A Verification

Run before the Stage A commit:

```powershell
python .\tools\check_document_pair_policy.py --root . --base-ref main --json
python .\tools\check_document_governance_rules.py --root . --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root . --json
.\tools\ci\local_gate.ps1 -StepTimeoutSeconds 1500 -Json
.\tools\ci\local_mr_review.ps1
```

## Stage B Verification

Run before Stage B local-main integration:

```powershell
python .\tools\check_embedded_codex_governance_alignment.py --root . --json
python .\tools\ci\run_python_tests.py --root . --pattern check_embedded_codex_governance_alignment.test.py
python .\tools\generate_operations_package.py --root . --package all --check --json
python .\tools\check_operations_package_docs.py --root . --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root . --json
.\tools\ci\local_gate.ps1 -StepTimeoutSeconds 1500 -Json
.\tools\ci\local_mr_review.ps1
```

## Current Status

<!-- CURRENT_STATUS_START -->
- Stage A runtime alignment plan is frozen as the authoritative runtime alignment contract.
- Stage B runtime checker implementation must follow this frozen plan before local-main integration.
- Durable team threshold was not met during Stage A because this is one write slice in `freeze-plan`; persistent execution must be re-evaluated for Stage B.
- Remote publication is not authorized.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Completed in this document: freeze the Stage A runtime alignment contract.
- Pending for Stage B: implement the runtime checker and tests from this plan.
- Pending for Stage B: register the checker in OpenSpec guard and CI manifest.
- Pending for Stage B: run local gates, local MR review, and stop at the remote-publication gate.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Stage A evidence is the local commit and local-main integration receipt produced for this frozen plan.
- Pending Stage B evidence: checker commit, rollback ref, completed claim, and cleanup record.
<!-- EVIDENCE_INDEX_END -->
