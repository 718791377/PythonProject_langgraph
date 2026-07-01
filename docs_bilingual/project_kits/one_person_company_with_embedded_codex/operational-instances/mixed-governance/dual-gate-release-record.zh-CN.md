---
doc_id: operational_instance_mixed_governance_dual_gate_release_record
lang: zh-CN
doc_class: operations_instance_pack
status: active
canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/mixed-governance/dual-gate-release-record.md
zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/mixed-governance/dual-gate-release-record.zh-CN.md
translation_of: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/mixed-governance/dual-gate-release-record.md
---
# 双门发布记录

## 目的

Records an actual release that requires both gates. 本文件是一份可填写的运行实例记录，不是第三本白皮书，也不是重新生成 48/60 正文运营包。

## 权威边界

当事项同时影响客户、收入或合规承诺以及代码、Agent 或 runtime 行为时，mixed governance 必须同时包含 business gate、Codex execution gate 和 human final approval。pricing、contracts、release、customer promises、financial commitments、legal commitments、remote publication 必须保留人类最终确认。

Canonical authority tokens: business gate; Codex execution gate; human final approval; pricing; contracts; release; customer promises; financial commitments; legal commitments; remote publication.

## 输入

- 同时影响 customer、revenue 或 compliance commitments 以及 code、Agent 或 runtime behavior 的事项。
- 业务证据和 Codex execution evidence。
- 裁剪模式、风险状态和人审上下文。

## 工具与技术

- 同时执行 business gate 与 Codex execution gate。
- 映射 pricing、contracts、release、customer promises、financial commitments、legal commitments、remote publication 影响。
- 任何外部承诺或 remote-publication 动作前保留 human final approval。

## 输出

- 包含双门、证据、决策和未决风险的 mixed-governance 记录。
- 可审计的 release、intake、impact、tailoring 或 portfolio review 记录。
- 带 linked business 与 Codex artifacts 的人审通过或阻断决定。

## 可填写记录

| 字段 | 值 |
| --- | --- |
| business gate | passed / blocked / not applicable |
| Codex execution gate | passed / blocked / not applicable |
| human final approval | approved / rejected / pending |
| affected_commitments | pricing / contracts / release / customer promises / financial commitments / legal commitments / remote publication |
| linked_docs | 路径 |

## 复盘备注

- 只记录属于本 operational instance 的 evidence。
- 通过 linked_docs 链接来源文件，不把无关真相复制进本文件。
- mixed 事项在承诺或 remote-publication 动作前必须升级到 mixed-governance instance pack。
