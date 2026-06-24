---
doc_id: shared_ledgers_decision_log
lang: en
doc_class: operations_runtime_pack
status: active
canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/shared-ledgers/decision-log.md
zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/shared-ledgers/decision-log.zh-CN.md
---
# Decision Log

## Purpose

This shared ledger records scoped business, Codex, and mixed decisions.

## Truth Boundary

This ledger may connect business truth and Codex execution truth, but it must never merge them into one authority. Every entry keeps scope, truth_owner, evidence_source, decision_right, and linked_docs visible.

## Required Fields

- scope
- truth_owner
- evidence_source
- decision_right
- linked_docs

## Operating Notes

- Use scope values: business, codex, or mixed.
- Use truth_owner values: founder, codex-operator, or human-review.
- Link customer, revenue, repo, runtime, Agent, legal, and evidence records without changing their truth owner.

## Inputs

- New event, decision, risk, evidence, review, or tailoring need.
- Required fields: scope, truth_owner, evidence_source, decision_right, linked_docs.

## Tools And Techniques

- Classify scope before writing facts.
- Separate business truth from Codex execution truth in the same record.
- Link source documents and runtime evidence instead of copying uncontrolled facts.

## Outputs

- One auditable ledger entry with owner, evidence, authority, and next action.
- A traceable record that supports later review, rollback, or monthly learning.
