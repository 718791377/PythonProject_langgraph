---
doc_id: one_person_company_embedded_codex_startup_matrix
lang: en
doc_class: product_lifecycle
status: active
canonical_path: docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.md
zh_cn_path: docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.zh-CN.md
---

# One-Person Company Embedded Codex Startup Matrix

## Purpose

This matrix makes Codex CLI personal production durable-team governance an embedded platform-governance capability inside the one-person-company operating system. The one-person company owns business truth. Codex owns execution truth. Shared ledgers connect evidence without merging authority.

Required vocabulary for every shared or mixed record:

- scope: business | codex | mixed
- truth_owner: founder | codex-operator | human-review
- evidence_source: customer | revenue | repo | runtime | agent | legal
- decision_right: human | delegated-draft-only
- linked_docs

Mixed customer/revenue/compliance plus code/agent/runtime work requires two-gate review: both the business gate and the Codex execution gate must pass before action.

## Startup Matrix

| one-person-company startup document | embedded Codex startup document | shared ledger | scope | truth_owner | evidence_source | decision_right | two-gate trigger | escalation note | linked docs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `company-thesis.md` | `thesis.md` | `decision-log.md` | business or codex | founder or codex-operator | customer or repo | human | Business purpose changes plus execution architecture changes. | Use human-review when positioning affects release promises. | linked docs |
| `offer.md` | `delivery-plan.md` | `decision-log.md` | mixed | human-review | customer, revenue, repo | human | Offer, price, or support commitment changes require code, agent, or release changes. | Business gate approves offer; Codex execution gate approves delivery path. | linked docs |
| `roadmap.md` | `delivery-plan.md` | `monthly-review.md` | mixed | human-review | customer, revenue, repo, runtime | human | Roadmap promise depends on repository or runtime delivery. | Keep customer commitment separate from local-main evidence. | linked docs |
| `risk-register.md` | `risk-register.md` | `risk-register.md` | business | founder | customer, legal, revenue | human | Business risk maps to platform risk. | One shared ledger row may contain business, codex, and mixed subrows. | linked docs |
| `agent-governance.md` | `agent-governance.md` | `agent-permissions.md` | codex | codex-operator | agent, repo, runtime | delegated-draft-only | Agent authority can affect customer-visible actions. | Escalate final promises to human-review. | linked docs |
| `support-playbook.md` | `incident-response.md` | `human-review-checklist.md` | mixed | human-review | customer, runtime, repo | human | Customer support issue requires code, runtime, or agent mitigation. | Business gate owns customer response; Codex execution gate owns fix evidence. | linked docs |
| `finance-model.md` | `observability.md` | `tracking-plan.md` | mixed | human-review | revenue, runtime, repo | human | Cost, revenue, or capacity model depends on runtime evidence. | Do not let platform metrics redefine revenue truth. | linked docs |
| `backup-restore.md` | `backup-restore.md` | `backup-restore.md` | mixed | human-review | legal, repo, runtime | human | Restore touches both customer/business records and repo-local durable state. | Restore business data and Codex durable state in separate sections. | linked docs |
| `monthly-review.md` | `monthly-review.md` | `monthly-review.md` | mixed | human-review | customer, revenue, repo, runtime, agent | human | Monthly review merges business learning and execution evidence. | Keep conclusions scoped as business, codex, or mixed. | linked docs |

## Process Group Usage

### Inputs

- One-person-company startup documents and the Codex 12-document startup order.
- Shared ledgers with scope, truth_owner, evidence_source, decision_right, and linked_docs fields.
- Current project tailoring mode and local-main evidence.

### Tools And Techniques

- Classify each item as business, codex, or mixed before writing a fact.
- Route business truth to founder-owned business files.
- Route execution truth to Codex platform-governance files.
- Route mixed matters through two-gate review: business gate plus Codex execution gate.

### Outputs

- A startup map that embeds Codex without making it a peer business authority.
- Shared ledgers that can be audited by scope and truth owner.
- Clear escalation notes for human-review and delegated-draft-only agent work.

## Stage B Embedded Governance Closeout

This Stage B closeout makes the nested relationship explicit: the one-person company owns business truth, and embedded Codex owns governed execution truth. Embedded Codex is not a peer business authority and must not redefine business truth.

- Codex boundary: Codex owns execution truth for agents, OpenSpec, worktrees, durable state, validation gates, local-main evidence, rollback, and release boundaries, while consuming business intent from the one-person company.
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
