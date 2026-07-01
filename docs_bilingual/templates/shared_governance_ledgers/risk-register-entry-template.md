---
doc_id: shared_governance_risk_register_entry_template
lang: en
doc_class: template
status: active
canonical_path: docs_bilingual/templates/shared_governance_ledgers/risk-register-entry-template.md
zh_cn_path: docs_bilingual/templates/shared_governance_ledgers/risk-register-entry-template.zh-CN.md
---
# Risk Register Entry Template

## Purpose

Record a business, codex, or mixed risk with evidence links. Use this template for shared governance ledgers inside a one-person-company project with embedded Codex platform governance.

## Required Fields

- id:
- date:
- title:
- owner:
- status:
- scope: business | codex | mixed
- truth_owner: founder | codex-operator | human-review
- evidence_source: customer | revenue | repo | runtime | agent | legal
- decision_right: human | delegated-draft-only
- linked_docs: []
- summary:
- next_action:

## Inputs

- Current business facts, Codex execution evidence, or mixed two-gate trigger.
- Customer, revenue, repo, runtime, agent, or legal evidence source.
- Related documents and prior decisions.

## Tools And Techniques

- Classify scope before writing facts.
- Assign truth_owner before recording conclusions.
- Link evidence rather than copying unrelated business truth into Codex files.
- Use human review when the record changes commitments, release gates, legal posture, or financial exposure.

## Outputs

- One ledger entry with scope, truth_owner, evidence_source, decision_right, linked_docs, summary, and next_action.
- A reviewable audit trail that keeps business truth and execution truth separate.
