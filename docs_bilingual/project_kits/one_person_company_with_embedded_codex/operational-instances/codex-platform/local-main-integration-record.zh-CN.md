---
doc_id: operational_instance_codex_platform_local_main_integration_record
lang: zh-CN
doc_class: operations_instance_pack
status: active
canonical_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/codex-platform/local-main-integration-record.md
zh_cn_path: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/codex-platform/local-main-integration-record.zh-CN.md
translation_of: docs_bilingual/project_kits/one_person_company_with_embedded_codex/operational-instances/codex-platform/local-main-integration-record.md
---
# 本地 main 集成记录

## 目的

Records local main integration evidence. 本文件是一份可填写的运行实例记录，不是第三本白皮书，也不是重新生成 48/60 正文运营包。

## 权威边界

Codex 拥有 execution truth：Agent routing、OpenSpec、worktree、durable state、validation gates、local-main evidence、rollback、release-boundary evidence。customers、revenue、pricing、contracts、legal posture、cashflow、refunds、customer promises 等 business truth 不进入 Codex 执行真相。

Canonical authority tokens: execution truth; Agent routing; OpenSpec; worktree; durable state; validation gates; local-main evidence; rollback; release-boundary.

## 输入

- Agent routing 请求、OpenSpec change、worktree 状态、durable state 或 runtime execution evidence。
- validation gates、local-main evidence、rollback 状态和 release-boundary 约束。
- 当执行可能影响外部承诺时关联 business 或 mixed 记录。

## 工具与技术

- 围绕 Agent routing、OpenSpec、worktree、durable state 审查 execution truth。
- 检查 validation、rollback、release-boundary 门。
- 当影响 pricing、contracts、customer promises、financial commitments、legal commitments 或 remote publication 时触发人审。

## 输出

- 带证据和门禁状态的 Codex execution 记录。
- local-main、validation、rollback、durable-state 或 release-boundary 输出。
- 当影响业务承诺时链接 mixed-governance 记录。

## 可填写记录

| 字段 | 值 |
| --- | --- |
| execution_scope | Agent routing / OpenSpec / worktree / durable state / validation gates |
| local_main_status | pending / merged / blocked |
| rollback_state | not-needed / prepared / executed |
| release_boundary | local-only / remote publication blocked / human approved |
| linked_business_or_mixed_docs | 路径 |

## 复盘备注

- 只记录属于本 operational instance 的 evidence。
- 通过 linked_docs 链接来源文件，不把无关真相复制进本文件。
- mixed 事项在承诺或 remote-publication 动作前必须升级到 mixed-governance instance pack。
