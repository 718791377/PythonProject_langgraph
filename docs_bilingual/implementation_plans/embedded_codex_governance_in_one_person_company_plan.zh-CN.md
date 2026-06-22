---
doc_id: embedded_codex_governance_in_one_person_company_plan
doc_class: implementation_plan
status: active
canonical_path: docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.md
zh_cn_path: docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.md
---
# Embedded Codex Governance In One-Person Company Forced Rename Plan - zh-CN Companion

## Purpose

This plan freezes the forced-unification implementation for embedding the Codex CLI personal production durable team inside the personal production one-person-company operating system.

The implementation regenerates the existing 48/60 body operations packages, force-renames semantically equivalent documents to the same canonical filename, updates registry entries, and blocks stale legacy names. It does not collapse package-specific body documents into a single body file because each package owns different truth.

## Governance Model

```text
one-person-company operating system
|- business governance: customers, revenue, pricing, contracts, support, delivery, cashflow
|- embedded Codex governance: agents, OpenSpec, worktrees, durable state, validation gates, release gates
`- shared governance ledgers: risk, decisions, metrics, evidence, review, permissions, human review
```

Business truth remains owned by the one-person-company project. Codex execution truth remains owned by the embedded durable-team governance surface. Mixed work must pass both business and Codex gates.

## Directory Decision

Keep the two generated body-package directories as the runtime truth:

- `docs_bilingual/operations_packages/codex_cli_durable_team/` - stores Codex durable-team generated body documents.
- `docs_bilingual/operations_packages/one_person_company/` - stores one-person-company generated body documents.

No shared body directory is introduced in this implementation. Shared semantics are expressed by the same canonical filename in each package directory, while package front matter, `doc_id`, purpose, authority boundary, and body text keep business truth and Codex execution truth separate.

## Forced Rename Set

The generator must change these source names and regenerate affected files:

| Package | Legacy name | Canonical name | Reason |
| --- | --- | --- | --- |
| both | `metrics.yaml` | `metrics.md` | Generated physical files and registry already use Markdown; source inventory must match. |
| one-person-company | `company-thesis.md` | `thesis.md` | Align the existence thesis slot across both packages. |
| Codex durable team | `agent-tool-policy.md` | `agent-governance.md` | Align the Agent governance slot across both packages. |
| one-person-company | `support-policy.md` | `support-playbook.md` | Align the support operating slot across both packages. |

The implementation may preserve other distinct names when they are not one-to-one equivalents, even if a semantic bridge exists. For example, `ops-playbook.md`, `tool-stack.md`, `automation-map.md`, `funnel-dashboard.md`, and `roadmap.md` remain package-specific unless a later plan creates directory-level subtypes to avoid collisions.

## Runtime Requirements

Update:

- `tools/generate_operations_package.py` - defines canonical generated operations-package inventories and renders body documents.
- `tools/check_operations_package_docs.py` - validates generated body documents, registry entries, and stale legacy names.
- `test/operations_package_docs.test.py` - covers generator and checker regression behavior.
- `docs_bilingual/docs_registry.yaml` - registers canonical generated document paths.
- `docs_bilingual/operations_packages/` - contains the regenerated operations-package body documents.

The checker must fail if generated operations-package directories still contain stale legacy files for `company-thesis`, `agent-tool-policy`, or `support-policy`. It must also fail if registry entries point to legacy paths or if generated content still uses `metrics.yaml` as the source list item.

## Verification

Run at minimum:

```powershell
python .\tools\generate_operations_package.py --root . --package all --check --json
python .\tools\check_operations_package_docs.py --root . --json
python .\tools\ci\run_python_tests.py --pattern operations_package_docs.test.py
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root . --json
```

Before local main integration, run local gate and local MR review. Stop before remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
- Stage A plan-freeze package is being prepared on branch `docs/force-unify-ops-packages`.
- Stage B runtime regeneration and forced rename must start only after this plan package is integrated into local `main`.
- Remote publication is not authorized.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Stage A: validate and commit this forced-rename governance plan.
- Stage A: integrate the plan package into local `main` and preserve the receipt that implementation may begin.
- Stage B: update the generator, checker, tests, registry, and generated operations-package documents.
- Stage B: regenerate the 48/60 logical body packages with canonical names and remove stale legacy generated paths.
- Closeout: run local gates, integrate into local `main`, clean the feature worktree, and stop at the remote-publication gate.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- `docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.md` - frozen English forced-rename implementation plan.
- `docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.zh-CN.md` - bilingual companion for the forced-rename implementation plan.
- `docs_bilingual/docs_registry.yaml` - registry entry for this implementation plan.
- pending implementation evidence: `tools/generate_operations_package.py`, `tools/check_operations_package_docs.py`, `test/operations_package_docs.test.py`, and regenerated `docs_bilingual/operations_packages/` outputs.
<!-- EVIDENCE_INDEX_END -->
