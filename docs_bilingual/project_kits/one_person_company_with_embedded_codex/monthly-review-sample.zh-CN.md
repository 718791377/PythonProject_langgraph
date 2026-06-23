---
doc_id: one_person_company_with_embedded_codex_monthly_review_sample
lang: zh-CN
doc_class: product_lifecycle
status: active
canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/monthly-review-sample.md
zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/monthly-review-sample.zh-CN.md
translation_of: docs_bilingual/project_kits/one_person_company_with_embedded_codex/monthly-review-sample.md
---
# 月度复盘样例

## 目的

把业务学习和平台执行证据一起复盘。 本页属于一人公司内嵌 Codex 项目包。

## 运营说明

- 每条事实先分类为 business、codex 或 mixed。
- 客户、收入、法务、支持、合同或现金流承诺走 business gate。
- 代码、Agent、worktree、durable state、runtime、验证和发布边界走 Codex execution gate。
- 两侧同时受影响时执行 mixed two-gate review。

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
