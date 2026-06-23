---
doc_id: one_person_company_with_embedded_codex_readme
lang: zh-CN
doc_class: product_lifecycle
status: active
canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/README.md
zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/README.zh-CN.md
translation_of: docs_bilingual/project_kits/one_person_company_with_embedded_codex/README.md
---
# 一人公司内嵌 Codex 项目包

## 目的

说明项目包目的、真相边界和使用方式。 本页属于一人公司内嵌 Codex 项目包。

## 项目包覆盖范围

- startup checklist
- folder structure
- governance gates
- local-main workflow
- remote-publication gate
- monthly review
- business gate
- Codex execution gate
- mixed two-gate review
- rollback

## 真相边界

业务真相覆盖客户、收入、定价、合同、支持、法务、现金流和业务学习。Codex 执行真相覆盖 Agent、OpenSpec、worktree、durable state、验证门、发布边界、local-main evidence 和 runtime evidence。共享台账通过 scope、truth_owner、evidence_source、decision_right 和 linked_docs 连接记录。

## 输入

- 当前项目范围、业务事实、Codex 执行证据和裁剪决策。
- 共享台账字段：scope、truth_owner、evidence_source、decision_right、linked_docs。
- local-main 状态、rollback 证据和 remote-publication gate 状态。

## 工具与技术

- 分离业务真相和 Codex 执行真相。
- 按 scope 应用 business gate、Codex execution gate 或 mixed two-gate review。
- Agent 工作保持 delegated-draft-only，除非人明确批准最终承诺。
- 声称执行工作已集成前，先记录 local-main evidence。

## 输出

- 可用于 startup checklist、folder structure、governance gates、local-main workflow、remote-publication gate 或 monthly review 的项目包页面。
- 业务治理与平台治理相互连接但不混淆的可审计证据。
