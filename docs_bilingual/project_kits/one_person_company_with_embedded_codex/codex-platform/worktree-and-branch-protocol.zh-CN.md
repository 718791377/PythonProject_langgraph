---
doc_id: codex_platform_worktree_and_branch_protocol
lang: zh-CN
doc_class: operations_runtime_pack
status: active
translation_of: docs_bilingual/project_kits/one_person_company_with_embedded_codex/codex-platform/worktree-and-branch-protocol.md
canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/codex-platform/worktree-and-branch-protocol.md
zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/codex-platform/worktree-and-branch-protocol.zh-CN.md
---
# Worktree And Branch Protocol

## Purpose

This Codex platform file governs isolated worktrees, branches, and local main.

## Execution Truth Boundary

Codex owns execution truth for Agent routing, OpenSpec, worktree isolation, durable state, local-main evidence, validation gates, rollback, release-boundary evidence, and remote-publication gate evidence. Codex does not own customers, revenue, pricing, contracts, legal commitments, cashflow, refunds, or customer promises.

## Required Gates

- Codex execution gate.
- Local validation gate.
- Local-main evidence gate.
- Rollback and release-boundary gate.
- Remote-publication approval gate when remote mutation is requested.

## Operating Notes

- Keep file ownership, changed paths, validation evidence, and rollback evidence explicit.
- Route only the smallest sufficient Agent or expert role set.
- Send mixed business impact through the business gate before final commitment.

## 输入

- Change scope, repo state, Agent routing context, OpenSpec state, worktree state, durable state, and linked evidence.
- Required gate state, validation evidence, rollback evidence, and linked_docs for the affected work.

## 工具与技术

- Use bounded delegation, explicit write ownership, and do-not-revert instructions.
- Run validation gates before local-main integration or release-boundary decisions.
- Record rollback evidence and remote-publication stop state when applicable.

## 输出

- A governed Codex execution record for the named platform surface.
- Clear evidence of gate status, owner, changed paths, rollback, and next action.

## zh-CN Companion Note

This zh-CN companion keeps ASCII-safe operating terms while preserving lang and translation_of metadata for bilingual pairing.
