---
doc_id: personal_production_one_person_company_operations_north_star
lang: en
canonical: docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md
translation_of: null
doc_class: north_star_plan
status: draft
---

# Personal Production One-Person Company Operations North Star

## Purpose

This North Star defines how a solo operator decides whether the one-person-company operating system is producing validated business progress without over-documenting low-risk work. It is separate from the Codex CLI durable-team platform North Star at `docs_bilingual/north_star_plan.md`.

## Evidence Boundary

This document is based on the Stage B fresh extraction run `one-person-company-pmi-refresh-stageb-20260619` over `Business Management/` and `PMP/`, plus the `one-person-company-pmi-refresh-stageb-product-lifecycle-20260619` full-document read of current lifecycle Markdown files. It records only aggregate evidence and repository-specific synthesis.

## Primary Metric

**Validated operating-loop throughput** is the count of operating loops that, within the review period:

1. start from customer evidence, business evidence, support evidence, financial evidence, or risk evidence;
2. pass the required tailoring gate for the affected layer, phase, or module;
3. produce a shipped, sold, supported, validated, or retired business output;
4. record human review for any governed-agent contribution that affects customer, revenue, legal, finance, release, or support commitments; and
5. feed learning into the next monthly review, metric contract, risk register, or operating playbook.

The metric counts validated loops, not raw tasks, words, commits, or agent messages.

## Input Metrics

| Input metric | What it measures | Example evidence |
| --- | --- | --- |
| Customer evidence loops | How often real customer or user evidence changes an offer, segment, product, support rule, or positioning decision | Interview notes, feedback triage, support tickets, adoption signals |
| Revenue and cash loops | Whether the business model, pricing, cashflow, and runway are reviewed before commitments grow | `pricing.md`, `finance-model.md`, `cashflow.md`, unit-economics note |
| Delivery stability loops | Whether shipped work is validated, supportable, and reversible | Validation note, release note, rollback note, issue log |
| Support-load loops | Whether support demand changes operations instead of staying hidden | Support policy, FAQ update, customer-success note |
| Learning cadence loops | Whether decisions and incidents become reusable learning | `monthly-review.md`, learning log, decision log |
| Governed-agent review loops | Whether AI-agent output that affects commitments is reviewed by the human owner | Agent review checklist, permission note, human sign-off |

## Guardrails

| Guardrail | Breach signal | Required response |
| --- | --- | --- |
| Unreviewed AI commitments | An agent drafts or sends customer, legal, finance, release, pricing, or support commitments without human review | Stop, review, and update `agent-governance.md` |
| Runway and cash risk | Cash, cost, or pricing assumptions become stale while commitments grow | Re-run finance review before expanding scope |
| Support risk | Delivery creates support obligations without support policy, FAQ, or escalation path | Expand operations layer before release or commitment |
| Privacy and compliance risk | Work touches personal data, sensitive data, contracts, regulated claims, or security boundaries | Expand governance and technical layers; do not stay lightweight |
| Over-documentation drag | Documentation grows without customer, revenue, risk, support, or learning value | Collapse to minimum sufficient documents and record the tailoring decision |

## Decision Thresholds

| Decision | Trigger | Action |
| --- | --- | --- |
| Use full architecture for affected scope | External users, money, sensitive data, compliance, trust, support obligation, repeated delivery, broad agent automation, or high rollback cost appears | Expand affected layers to full I/T/O, owner, risk, validation, release/rollback, and retrospective evidence |
| Keep whole-project lightweight | Work is private, reversible, low-risk, has one owner, and has no external users, money, sensitive data, support promise, shared runtime, or release commitment | Use the 12 minimal startup documents or compact equivalents plus validation and learning notes |
| Use phase-local lightweight | Discovery, prototype, interview, content exploration, or metrics exploration is low risk inside a larger governed effort | Keep lightness inside that phase and define expansion triggers |
| Use module-level lightweight | A bounded module is reversible and does not change the operating model, trust boundary, customer promise, durable state, public API, or release safety | Keep module I/T/O, owner, validation, rollback or deletion path, and learning note |
| Use hybrid | Uncertainty is high but likely delivery may affect production, users, revenue, trust, compliance, runtime behavior, or release safety | Start adaptive; freeze predictive process-group controls before external impact |
| Stop or pivot | Loops produce repeated negative evidence, no customer pull, runway pressure, support overload, or unresolved trust/compliance risk | Stop, pivot, or reduce scope before adding more documents or automation |

## Process-Group Operating Cadence

| Process group | Inputs | Tools and Techniques | Outputs |
| --- | --- | --- | --- |
| Initiating | Customer or operating signal, candidate loop, current tailoring state, owner capacity | Value framing, risk scan, stop-condition framing | Loop charter, owner, initial tailoring decision |
| Planning | Loop charter, 12-layer impact, cash/support constraints, agent boundary | Tailoring scorecard, validation design, human-review design | Loop plan, input metrics, guardrails, validation path |
| Executing | Approved loop plan, minimal documents, agent permissions, customer or operating evidence | Discovery, shipping, selling, supporting, measuring, governed-agent drafting | Loop output, evidence packet, changed document or operating asset |
| Monitoring and Controlling | Metrics, support load, cash/runway signal, risk register, agent review evidence | Metric review, guardrail review, change control, rollback/stop review | Continue/expand/stop decision, issue updates, guardrail response |
| Closing | Loop output, decision, learning, residual risk | Monthly review, decision archive, playbook update, next-cycle prioritization | Archived loop, updated policy or metric, next-cycle input |

## Non-Goals

- Do not treat this North Star as a task list.
- Do not measure agent activity as business progress unless it passes human and operating-loop validation.
- Do not use this North Star to replace project-specific customer, finance, legal, support, or release records.
