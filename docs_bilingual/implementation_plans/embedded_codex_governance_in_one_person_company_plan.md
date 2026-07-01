---
doc_id: embedded_codex_governance_in_one_person_company_plan
doc_class: implementation_plan
status: final
canonical_path: docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.md
zh_cn_path: docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.zh-CN.md
---
# Embedded Codex Governance In One-Person Company Forced Rename Plan

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
| both | legacy machine-readable metrics filename | `metrics.md` | Generated physical files and registry already use Markdown; source inventory must match. |
| one-person-company | legacy company-specific thesis filename | `thesis.md` | Align the existence thesis slot across both packages. |
| Codex durable team | legacy Agent governance filename | `agent-governance.md` | Align the Agent governance slot across both packages. |
| one-person-company | legacy support governance filename | `support-playbook.md` | Align the support operating slot across both packages. |

The implementation may preserve other distinct names when they are not one-to-one equivalents, even if a semantic bridge exists. For example, `ops-playbook.md`, `tool-stack.md`, `automation-map.md`, `funnel-dashboard.md`, and `roadmap.md` remain package-specific unless a later plan creates directory-level subtypes to avoid collisions.

## Runtime Requirements

Update:

- `tools/generate_operations_package.py` - defines canonical generated operations-package inventories and renders body documents.
- `tools/check_operations_package_docs.py` - validates generated body documents, registry entries, and stale legacy names.
- `test/operations_package_docs.test.py` - covers generator and checker regression behavior.
- `docs_bilingual/docs_registry.yaml` - registers canonical generated document paths.
- `docs_bilingual/operations_packages/` - contains the regenerated operations-package body documents.
- `docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.md` - records the embedded-governance truth boundary and links the white paper, North Star, implementation plan, registry, and separated operations-package directories.
- `docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.md` - links the detailed embedded-governance policy from the one-person-company operating-system narrative.
- `docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md` - links the detailed policy from the mixed-loop counting gate.

The checker must fail if generated operations-package directories still contain stale legacy thesis, Agent governance, or support governance generated files. It must also fail if registry entries point to legacy paths or if generated content still uses the legacy machine-readable metrics source list item.

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
- Stage A governance package is integrated into local `main` at `7cf8dba` and recorded the implementation-confirmation gate.
- Stage B runtime regeneration and forced canonical rename are integrated into local `main` at `75ccbb4`.
- Generated body packages remain separated by package directory; shared semantics use shared canonical filenames only.
- Remote publication is not authorized and has not been performed.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Completed: Stage A validated and integrated the forced-rename governance plan.
- Completed: Stage A preserved the confirmation receipt that allowed implementation to begin.
- Completed: Stage B updated the generator, checker, tests, registry, and generated operations-package documents.
- Completed: Stage B regenerated the 48/60 logical body packages with canonical names and removed stale legacy generated paths.
- Completed: local gates passed, local `main` was updated, the feature worktree was cleaned, and execution stopped at the remote-publication gate.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- `7cf8dba` - local `main` commit that activated the Stage A governance plan for implementation confirmation.
- `75ccbb4` - local `main` commit that regenerated the 48/60 operations-package body documents and canonical naming runtime.
- `.omx/session-claims/completed/implement-force-unify-ops-packages-stageb.json` - completed claim and cleanup record.
- `refs/backup/local-main/20260623-024252-before-implement-force-unify-ops-packages-stageb` - rollback ref before Stage B local-main integration.
- `tools/generate_operations_package.py` - canonical generated operations-package inventories and renderer.
- `tools/check_operations_package_docs.py` - generated package, registry, and stale-name guard.
- `test/operations_package_docs.test.py` - regression coverage for generation, stale names, registry drift, and package isolation.
- `docs_bilingual/operations_packages/` - regenerated package-specific body documents.
<!-- EVIDENCE_INDEX_END -->
