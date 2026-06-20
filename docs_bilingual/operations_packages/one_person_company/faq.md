---
doc_id: one_person_company_faq
doc_class: operations_package
status: active
package: one-person-company
body_kind: operations_and_customer_success_body
generated_by: tools/generate_operations_package.py
lang: en
---

<!-- GENERATED_BY: tools/generate_operations_package.py; DO NOT EDIT BY HAND. -->

# One-Person Company FAQ Body Document

## Purpose

Defines how the solo production business operating system uses the faq.md artifact inside the operations and customer success family to make decisions, collect evidence, and select the right tailoring depth.

## Authority Boundary

- Authority sources: operations white paper, North Star, Business Management synthesis, product lifecycle registers, PMI process-group contract, and tailoring rules.
- This document operationalizes only this solo business operations package.
- Any external commitment, revenue, contract, privacy, or compliance impact must enter a fuller governance depth.

## Lifecycle Placement

- Primary lifecycle layers: L10 Operations, L8 Execution
- Primary process groups: Executing, Monitoring and Controlling, Closing
- Owner surface: Operations Office
- Document family: Operations and customer success; source list item: `faq.md`.

## Tailoring Rules

Default tailoring mode: Hybrid architecture. This choice must explain why it is not heavier or lighter and must keep escalation triggers visible.

| Mode | Use when | Lightweight scope |
| --- | --- | --- |
| Full architecture | Cross-stage, external-customer, revenue, compliance, security, publication, rollback, durable-state, shared-runtime, or multi-agent work. | Govern every affected risk layer end to end. |
| Whole-project lightweight | Private, reversible, low-risk exploration with no external commitment, durable-state impact, publication, sensitive data, or shared runtime. | The whole project may stay light while still recording owner, validation, rollback, and learning. |
| Phase-local lightweight | One discovery, metrics, growth, or retrospective phase is low risk inside a larger governed project. | Only that named phase is light; upstream and downstream gates stay explicit. |
| Module-level lightweight | One bounded document family, helper, prototype, or local module does not change trust, state, public API, CI, release, or shared runtime behavior. | Only that module is light; the surrounding project keeps its full boundary. |
| Hybrid architecture | Most real work, where low-risk phases can start light but production, customer, revenue, trust, durable-state, or release impact needs fuller control. | Critical layers are full; low-risk phases or modules stay light until escalation triggers fire. |

### Why this mode is not heavier or lighter

`faq.md` uses the default mode because the operations and customer success family needs governed evidence, but a heavier mode is reserved for external commitment, sensitive information, shared state, or difficult recovery.

### Escalation triggers

Escalate to a heavier tailoring mode when scope, trust, compliance, revenue exposure, recovery difficulty, or cross-boundary coordination exceeds the assumptions recorded for the current mode. For `faq.md`, also escalate when the owner cannot confirm evidence, validation is no longer repeatable, or outputs affect an external commitment.

## Inputs

- Current offer, customers, cashflow, delivery capacity, risk, compliance, and Operations Office owner constraints.
- The `faq.md` document family, business assumptions, evidence sources, dependencies, and stop or expand conditions.
- Solo-operator time budget, automation boundary, and monthly review inputs.

## Tools And Techniques

- Twelve-layer placement, responsibility-domain mapping, PMI process-group I/T/O, agile feedback loops, and tailoring scorecard.
- Customer discovery, finance checks, channel experiments, service delivery review, and compliance checks.
- Governance depth escalates only when external commitment, revenue, or risk expands.

## Outputs

- Governed `FAQ` body document, zh-CN companion, and registry entry.
- Next update for offer, pricing, channel, support, finance, compliance, or knowledge base.
- Evidence for monthly keep, stop, pivot, expand, or re-tailor decisions.

## Process Group Operating Table

| Process group | Inputs | Tools And Techniques | Outputs |
| --- | --- | --- | --- |
| Initiating | source need, owner signal, scope boundary, first risk; document `faq.md` | charter framing, stakeholder scan, tailoring pre-check | authorized operating slice, named owner, initial risk log |
| Planning | approved purpose, dependencies, constraints, acceptance target; document `faq.md` | I/T/O planning, RACI mapping, validation design, rollback design | document plan, validation path, rollback boundary |
| Executing | approved slice, templates, evidence, local state; document `faq.md` | controlled drafting, review, test, evidence capture | updated operating artifact, change evidence, handoff record |
| Monitoring and Controlling | active artifact, metrics, issues, review feedback; document `faq.md` | quality checks, variance review, change control, gate rerun | issue log, decision record, gate evidence |
| Closing | accepted artifact, final evidence, residual risk; document `faq.md` | closeout review, archive or registry sync, retrospective | final body doc, registry entry, lessons learned |

## Closeout And Registry

- Registry `doc_id` remains unique: `one_person_company_faq`.
- English primary `docs_bilingual/operations_packages/one_person_company/faq.md` and zh-CN companion `docs_bilingual/operations_packages/one_person_company/faq.zh-CN.md` stay paired.
- Closeout confirms owner, tailoring mode, escalation triggers, output evidence, and next-cycle input.
