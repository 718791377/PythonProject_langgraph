---
doc_id: operational_instance_business_operations_sales_support_refund_case_record
lang: zh-CN
doc_class: operations_instance_pack
status: active
canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/business-operations/sales-support-refund-case-record.md
zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/business-operations/sales-support-refund-case-record.zh-CN.md
translation_of: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/business-operations/sales-support-refund-case-record.md
---
# 销售支持退款案例记录

## 目的

Records actual sales, support, refund, and escalation cases. 本文件是一份可填写的运行实例记录，不是第三本白皮书，也不是重新生成 48/60 正文运营包。

## 权威边界

一人公司拥有 business truth：customers、revenue、pricing、contracts、legal posture、cashflow、support、refunds、delivery commitments、business learning。Codex execution truth 仍受 Agent permissions、runtime validation、durable-state recovery、local-main evidence、rollback gates、remote-publication gates 保护。

Canonical authority tokens: business truth; customers; revenue; pricing; contracts; legal posture; cashflow; support; refunds; delivery commitments; business learning; must not bypass Agent permissions; runtime validation; durable-state recovery; local-main evidence; rollback gates; remote-publication gates.

## 输入

- customer、revenue、pricing、contract、legal、cashflow、support、refund、delivery 或 learning 证据。
- 当业务决策需要代码、Agent 或 runtime 变化时关联 Codex execution records。
- 不可委派承诺的人审上下文。

## 工具与技术

- 围绕 customers、revenue、pricing、contracts、legal posture、cashflow、support、refunds、delivery commitments、business learning 审查 business truth。
- 审查 full、whole-project lightweight、phase-local lightweight、module-level lightweight 或 hybrid 裁剪模式。
- 当业务结果需要 Codex 执行工作时升级到 dual-gate。

## 输出

- 带证据、owner、decision 和 next action 的业务运营记录。
- 需要 runtime 工作时链接 mixed-governance 或 Codex intake。
- 经人确认且 must not bypass Agent permissions、runtime validation、durable-state recovery、local-main evidence、rollback gates、remote-publication gates 的业务承诺。

## 可填写记录

| 字段 | 值 |
| --- | --- |
| business_scope | customers / revenue / pricing / contracts / legal posture / cashflow / support / refunds / delivery commitments / business learning |
| human_decision | approved / rejected / deferred |
| codex_dependency | none / intake required / mixed dual-gate required |
| gate_note | must not bypass Agent permissions, runtime validation, durable-state recovery, local-main evidence, rollback gates, or remote-publication gates |
| linked_docs | 路径 |

## 复盘备注

- 只记录属于本 operational instance 的 evidence。
- 通过 linked_docs 链接来源文件，不把无关真相复制进本文件。
- mixed 事项在承诺或 remote-publication 动作前必须升级到 mixed-governance instance pack。
