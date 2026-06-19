---
change_id: generate-operations-package-runtime-20260620
lang: zh-CN
status: proposed
owner: codex
created_at: 2026-06-20
translation_of: openspec/changes/generate-operations-package-runtime-20260620/proposal.md
---

# 提案：生成运营包与 Runtime

## 为什么

`Codex CLI 个人开发者生产级持久化团队` 与 `个人级生产级一人公司运营` 已经具备白皮书、北极星、清单图、生命周期规则、PMI 覆盖和裁剪原则。当前缺口是把这些规范清单转成受治理、可检查、双语成对的运营包文件，并提供可重复运行的 live runtime 来生成和校验这些运营包。

用户明确要求两阶段本地 main 优先交付：先冻结方案并合入本地 `main`，再按照冻结方案实现 live runtime 并再次合入本地 `main`。

## 变更内容

- 冻结一份双语实施方案，作为运营包生成和 runtime 交付依据。
- 新增 OpenSpec delta requirement，覆盖运营包生成、裁剪决策、过程组式 I/T/O、双语 registry 覆盖和本地 main 优先阶段化交付。
- 在 runtime 修改前明确 Stage B 范围：确定性生成器、检查器、测试、registry 更新和生成的双语运营包文档。
- 要求所有执行层面的流程在生成或校验文档中显式具备 `Inputs`、`Tools And Techniques`、`Outputs`，中文伴随文件使用 `输入`、`工具与技术`、`输出`。
- 明确裁剪规则：完整架构、全项目轻量、阶段局部轻量、模块级轻量和混合架构。
- 除非用户后续显式要求远端发布，否则远端发布不在范围内。

## 非范围

- Stage B 不重新读取原始 Business Management 或 PMP 资料库；当前目标是运营化已经刷新的语料体系。
- 不推送 GitLab/GitHub，不创建/更新/合并 GitLab MR，不同步 GitHub，也不修改远端引用。
- 不替换现有白皮书、北极星或清单图的权威地位。
