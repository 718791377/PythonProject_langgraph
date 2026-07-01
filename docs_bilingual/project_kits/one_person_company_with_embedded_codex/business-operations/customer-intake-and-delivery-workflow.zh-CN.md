---
doc_id: business_operations_customer_intake_and_delivery_workflow
lang: zh-CN
doc_class: operations_runtime_pack
status: active
translation_of: docs_bilingual/project_kits/one_person_company_with_embedded_codex/business-operations/customer-intake-and-delivery-workflow.md
canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/business-operations/customer-intake-and-delivery-workflow.md
zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/business-operations/customer-intake-and-delivery-workflow.zh-CN.md
---
# Customer Intake And Delivery Workflow

## Purpose

This business operations file governs customer intake and delivery commitments.

## Business Truth Boundary

The one-person company owns business truth for customers, revenue, pricing, contracts, legal posture, cashflow, support, refunds, delivery commitments, and business learning. Business operations may request Codex execution, but they must not bypass Agent permissions, runtime validation, durable-state recovery, local-main evidence, rollback gates, or remote-publication gates.

## Required Gates

- Business gate.
- Human approval gate for pricing, contracts, legal commitments, customer promises, refunds, or financial commitments.
- Mixed dual gate when business commitments and execution behavior both change.

## Operating Notes

- Keep customer, revenue, offer, legal, cashflow, support, refund, and delivery facts under founder or human-review authority.
- Use Codex evidence only as execution readiness proof.
- Stop when execution readiness is not proven for a promised outcome.

## 输入

- Current business scope, customer facts, finance facts, legal facts, support facts, linked evidence, and affected commitments.
- Required approvals, linked_docs, and execution-readiness evidence when delivery depends on runtime behavior.

## 工具与技术

- Use human review for final non-delegable business commitments.
- Trace evidence before changing customer, legal, pricing, refund, support, or finance posture.
- Escalate to mixed governance when code, Agent, or runtime behavior affects the commitment.

## 输出

- A business operating record for the named topic.
- A clear approval, stop, escalation, handoff, or review result with linked evidence.

## zh-CN Companion Note

This zh-CN companion keeps ASCII-safe operating terms while preserving lang and translation_of metadata for bilingual pairing.
