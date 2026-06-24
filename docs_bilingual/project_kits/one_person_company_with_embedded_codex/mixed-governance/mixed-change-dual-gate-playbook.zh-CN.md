---
doc_id: mixed_governance_mixed_change_dual_gate_playbook
lang: zh-CN
doc_class: operations_runtime_pack
status: active
translation_of: docs_bilingual/project_kits/one_person_company_with_embedded_codex/mixed-governance/mixed-change-dual-gate-playbook.md
canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/mixed-governance/mixed-change-dual-gate-playbook.md
zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/mixed-governance/mixed-change-dual-gate-playbook.zh-CN.md
---
# Mixed Change Dual Gate Playbook

## Purpose

This mixed governance file defines dual-gate handling for mixed changes.

## Mixed Governance Boundary

Use this file when one change affects both business commitments and Codex execution behavior. Require both the business gate and the Codex execution gate before final approval. Preserve human final approval for pricing, contracts, release, customer promises, financial commitments, legal commitments, and remote publication.

## Required Gates

- business gate.
- Codex execution gate.
- human final approval gate for non-delegable mixed decisions.

## Operating Notes

- Translate business intent into execution constraints without transferring truth ownership.
- Translate execution change impact back into customer, legal, pricing, finance, support, or delivery implications.
- Stop when either gate is missing or the evidence chain is incomplete.

## 输入

- Current mixed scope, linked business facts, linked execution evidence, affected commitments, and runtime impact.
- Gate status, human approval needs, and linked_docs across both sides.

## 工具与技术

- Run dual-gate review with explicit owner, evidence, stop conditions, and approval authority.
- Keep business truth and execution truth in separate statements inside the same brief.
- Use shared ledgers to trace decisions, risks, evidence, and human review.

## 输出

- A mixed-governance record with both gates visible.
- A clear approval, stop, escalation, or handoff result.

## zh-CN Companion Note

This zh-CN companion keeps ASCII-safe operating terms while preserving lang and translation_of metadata for bilingual pairing.
