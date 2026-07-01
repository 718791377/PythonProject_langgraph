---
doc_id: operational_instance_shared_ledgers_evidence_register_instance
lang: en
doc_class: operations_instance_pack
status: active
canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/shared-ledgers/evidence-register.instance.md
zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/shared-ledgers/evidence-register.instance.zh-CN.md
---
# Evidence Register Instance

## Purpose

Records actual customer, revenue, repo, runtime, agent, and legal evidence. This file is a fillable record for one operational instance, not a third white paper and not a regenerated 48/60 operations package.

## Authority Boundary

This shared ledger can connect business truth, Codex execution truth, and mixed evidence only when every row keeps scope, truth_owner, evidence_source, decision_right, and linked_docs explicit.

Canonical authority tokens: business truth; Codex execution truth; mixed; scope; truth_owner; evidence_source; decision_right; linked_docs.

## Inputs

- A scoped business, Codex, or mixed event that needs a durable record.
- Evidence from customer, revenue, repo, runtime, agent, legal, or review sources.
- The current human review and decision-right boundary.

## Tools And Techniques

- Ledger row classification by scope: business, codex, or mixed.
- Truth-owner mapping and linked-doc traceability.
- Human review for non-delegable decisions and mixed authority boundaries.

## Outputs

- A fillable record row with scope, truth_owner, evidence_source, decision_right, and linked_docs.
- A traceable decision, risk, evidence, tailoring, human-review, or monthly-review entry.
- A clear separation between business truth, Codex execution truth, and mixed evidence.

## Fillable Record

| Field | Value |
| --- | --- |
| scope | business | codex | mixed |
| truth_owner | founder | codex-operator | human-review |
| evidence_source | customer | revenue | repo | runtime | agent | legal | review |
| decision_right | human | delegated-draft-only |
| linked_docs | list related ledgers, runtime records, business records, or mixed-gate records |

## Review Notes

- Record only evidence that belongs to this instance.
- Link source documents instead of copying unrelated truth into this file.
- Escalate mixed items to the mixed-governance instance pack before commitments or remote-publication actions.
