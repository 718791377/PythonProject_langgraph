---
doc_id: shared_governance_risk_register_entry_template
lang: zh-CN
doc_class: template
status: active
canonical_path: docs_bilingual/templates/shared_governance_ledgers/risk-register-entry-template.md
zh_cn_path: docs_bilingual/templates/shared_governance_ledgers/risk-register-entry-template.zh-CN.md
translation_of: docs_bilingual/templates/shared_governance_ledgers/risk-register-entry-template.md
---
# 风险登记条目模板

## 目的

记录带证据链接的业务、Codex 或混合风险。 本模板用于一人公司项目内嵌 Codex 平台治理时的共享治理台账。

## 必填字段

- id:
- date:
- title:
- owner:
- status:
- scope: business | codex | mixed
- truth_owner: founder | codex-operator | human-review
- evidence_source: customer | revenue | repo | runtime | agent | legal
- decision_right: human | delegated-draft-only
- linked_docs: []
- summary:
- next_action:

## 输入

- 当前业务事实、Codex 执行证据或 mixed two-gate 触发器。
- customer、revenue、repo、runtime、agent 或 legal 证据来源。
- 关联文档和历史决策。

## 工具与技术

- 写入事实前先分类 scope。
- 记录结论前先指定 truth_owner。
- 链接证据，不把无关业务真相复制到 Codex 文件。
- 影响承诺、发布门、法务姿态或财务暴露时必须 human-review。

## 输出

- 一条包含 scope、truth_owner、evidence_source、decision_right、linked_docs、summary 和 next_action 的台账记录。
- 可审计且不混用业务真相与执行真相的证据链。
