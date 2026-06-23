---
doc_id: tailoring_decision_record_template
lang: zh-CN
doc_class: template
status: active
canonical_path: docs_bilingual/templates/tailoring_decision_record_template.md
zh_cn_path: docs_bilingual/templates/tailoring_decision_record_template.zh-CN.md
translation_of: docs_bilingual/templates/tailoring_decision_record_template.md
---
# 裁剪决策记录模板

## 目的

本模板记录一人公司内嵌 Codex 治理项目为什么采用完整、轻量、按模块裁剪、分阶段或应急收敛的运营模式。

## 必填字段

- id:
- date:
- owner:
- mode: full | light | module-tailored | phased | emergency-contained
- why_not_heavier:
- why_not_lighter:
- escalation_triggers:
- rollback:
- local_main_evidence:
- linked_docs: []

## 输入

- 项目规模、客户影响、合规暴露、收入影响、代码影响、Agent 影响、runtime 影响和 durable-state 影响。
- 当前 business gate、Codex execution gate 以及任何 two-gate 触发器。
- 现有 local-main evidence 和 rollback 证据。

## 工具与技术

- 选择仍能保护业务真相和执行真相的最轻模式。
- 说明 why_not_heavier 和 why_not_lighter，使裁剪可审计。
- 工作开始前定义 escalation_triggers。
- 明确 rollback 和 local_main_evidence。

## 输出

- 已记录的裁剪模式和理由。
- 升级到完整架构或降级到轻量本地路径的清晰触发条件。
- 模块级风险可以按模块裁剪，但混合事项仍执行 two-gate 的证据。
