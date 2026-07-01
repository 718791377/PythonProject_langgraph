---
doc_id: one_person_company_with_embedded_codex_local_main_workflow
lang: en
doc_class: product_lifecycle
status: active
canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/local-main-workflow.md
zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/local-main-workflow.zh-CN.md
---

# Local-Main Workflow

## Purpose

Use local-main-first validation, merge workflow, and rollback evidence. This page belongs to the one-person-company with embedded Codex project kit.

## Operating Notes

- Classify every fact as business, codex, or mixed.
- Use the business gate for customer, revenue, legal, support, contract, or cashflow commitments.
- Use the Codex execution gate for code, Agent, worktree, durable state, runtime, validation, and release-boundary work.
- Use mixed two-gate review when both sides are affected.

## Inputs

- Current project scope, business facts, Codex execution evidence, and tailoring decision.
- Shared ledger fields: scope, truth_owner, evidence_source, decision_right, linked_docs.
- Local-main status, rollback evidence, and remote-publication gate status.

## Tools And Techniques

- Separate business truth from Codex execution truth.
- Apply business gate, Codex execution gate, or mixed two-gate review based on scope.
- Keep Agent work delegated-draft-only unless a human explicitly approves the final commitment.
- Record local-main evidence before claiming integrated execution work.

## Outputs

- A usable project-kit page for startup checklist, folder structure, governance gates, local-main workflow, remote-publication gate, or monthly review.
- Auditable evidence that business and platform governance remain connected but not confused.

## Stage B Embedded Governance Closeout

This Stage B closeout makes the nested relationship explicit: the one-person company owns business truth, and embedded Codex owns governed execution truth. Embedded Codex is not a peer business authority and must not redefine business truth.

- One-person company boundary: the one-person company owns business truth for customers, revenue, pricing, contracts, legal posture, cashflow, support, delivery commitments, and business learning; embedded Codex supplies execution evidence and automation support.
- Tailoring modes: full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, and hybrid are all scoped choices. Tailoring does not delete the twelve-layer mental model; it only changes how much evidence and ceremony is required for the chosen project, phase, module, or release slice.
- Bridge rule: the 10-layer runtime capability view is an implementation projection of the 12-layer lifecycle view. The bridge prevents runtime convenience from overriding lifecycle authority.

### Inputs

- Current business intent, execution evidence, registry entry, tailoring decision, and local-main / remote-publication boundary.
- Business truth inputs when customers, revenue, pricing, contracts, legal posture, cashflow, support, delivery commitments, or business learning are affected.
- Execution truth inputs when agent routing, OpenSpec, worktree isolation, durable state, validation, rollback, or release boundaries are affected.

### Tools And Techniques

- Apply the shared truth-boundary map before selecting full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, or hybrid mode.
- Use process-group I/T/O, RACI ownership, evidence traceability, validation gates, and escalation triggers instead of deleting layers.
- Route mixed changes through both the business gate and the Codex execution gate before local-main integration or remote publication.

### Outputs

- A scoped governance mode, updated evidence trail, linked registry entry, and explicit owner for business truth, execution truth, or mixed truth.
- A closeout decision that either stays lightweight in the declared scope, escalates to fuller architecture, or stops at the publication gate until human approval.
