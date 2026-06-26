---
doc_id: operational_instance_shared_ledgers_evidence_register_instance
lang: zh-CN
doc_class: operations_instance_pack
status: active
canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/shared-ledgers/evidence-register.instance.md
zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/shared-ledgers/evidence-register.instance.zh-CN.md
translation_of: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/shared-ledgers/evidence-register.instance.md
---
# 证据登记册实例

## 目的

Records actual customer, revenue, repo, runtime, agent, and legal evidence. 本文件是一份可填写的运行实例记录，不是第三本白皮书，也不是重新生成 48/60 正文运营包。

## 权威边界

本共享台账可以连接 business truth、Codex execution truth 与 mixed evidence，但每一行都必须显式保留 scope、truth_owner、evidence_source、decision_right、linked_docs。

Canonical authority tokens: business truth; Codex execution truth; mixed; scope; truth_owner; evidence_source; decision_right; linked_docs.

## 输入

- 需要沉淀记录的 business、codex 或 mixed 事项。
- 来自 customer、revenue、repo、runtime、agent、legal 或 review 的证据。
- 当前人审和 decision_right 边界。

## 工具与技术

- 按 scope: business | codex | mixed 分类台账行。
- 映射 truth_owner 并维护 linked_docs 可追踪性。
- 对不可委派决策和 mixed 权威边界执行人审。

## 输出

- 包含 scope、truth_owner、evidence_source、decision_right、linked_docs 的可填写记录行。
- 可追踪的决策、风险、证据、裁剪、人审或月度复盘条目。
- business truth、Codex execution truth 与 mixed evidence 的清晰分离。

## 可填写记录

| 字段 | 值 |
| --- | --- |
| scope | business | codex | mixed |
| truth_owner | founder | codex-operator | human-review |
| evidence_source | customer | revenue | repo | runtime | agent | legal | review |
| decision_right | human | delegated-draft-only |
| linked_docs | list related ledgers, runtime records, business records, or mixed-gate records |

## 复盘备注

- 只记录属于本 operational instance 的 evidence。
- 通过 linked_docs 链接来源文件，不把无关真相复制进本文件。
- mixed 事项在承诺或 remote-publication 动作前必须升级到 mixed-governance instance pack。
