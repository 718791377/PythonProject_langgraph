---
doc_id: operational_instance_codex_platform_runtime_run_record
lang: en
doc_class: operations_instance_pack
status: active
canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/codex-platform/runtime-run-record.md
zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/codex-platform/runtime-run-record.zh-CN.md
---
# Runtime Run Record

## Purpose

Records an actual Agent or runtime execution. This file is a fillable record for one operational instance, not a third white paper and not a regenerated 48/60 operations package.

## Authority Boundary

Codex owns execution truth for Agent routing, OpenSpec, worktree isolation, durable state, validation gates, local-main evidence, rollback, and release-boundary evidence. Business truth for customers, revenue, pricing, contracts, legal posture, cashflow, refunds, and customer promises remains outside this Codex record.

Canonical authority tokens: execution truth; Agent routing; OpenSpec; worktree; durable state; validation gates; local-main evidence; rollback; release-boundary.

## Inputs

- Agent routing request, OpenSpec change, worktree state, durable state, or runtime execution evidence.
- Validation gates, local-main evidence, rollback state, and release-boundary constraints.
- Linked business or mixed records when execution may affect external commitments.

## Tools And Techniques

- Execution-truth review across Agent routing, OpenSpec, worktree, and durable state.
- Validation, rollback, and release-boundary gate checks.
- Human review whenever execution affects pricing, contracts, customer promises, financial commitments, legal commitments, or remote publication.

## Outputs

- A Codex execution record with evidence and gate status.
- Local-main, validation, rollback, durable-state, or release-boundary outputs.
- Linked mixed-governance records when business commitments are affected.

## Fillable Record

| Field | Value |
| --- | --- |
| execution_scope | Agent routing / OpenSpec / worktree / durable state / validation gates |
| local_main_status | pending / merged / blocked |
| rollback_state | not-needed / prepared / executed |
| release_boundary | local-only / remote publication blocked / human approved |
| linked_business_or_mixed_docs | paths |

## Review Notes

- Record only evidence that belongs to this instance.
- Link source documents instead of copying unrelated truth into this file.
- Escalate mixed items to the mixed-governance instance pack before commitments or remote-publication actions.
