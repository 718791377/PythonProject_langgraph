---
change_id: expand-operations-package-full-body-doc-generation-20260620
status: proposed
owner: codex
created_at: 2026-06-20
lang: zh-CN
translation_of: openspec/changes/expand-operations-package-full-body-doc-generation-20260620/proposal.md
---

# 提案：把运营包扩展为正文级文档生成

## 为什么

当前运营包 runtime 已经证明了确定性生成、检查器、registry 覆盖、裁剪语言以及过程组式 Inputs / Tools And Techniques / Outputs。但它主要生成的是两套运营系统周围的治理与登记层，还没有真正生成全部正文级运营文件。用户现在要求下一阶段生成实际正文：

- Codex CLI 个人开发者生产级持久化团队：48 个核心正文文档，每个都有英文主文档和 zh-CN 伴随文件。
- 个人级生产级一人公司运营：60 个核心正文文档，每个都有英文主文档和 zh-CN 伴随文件。

因此，48 和 60 必须成为真实生成的正文文档数量，而不只是登记表中的数字。

## 变更内容

- 冻结一份双语的正文级运营包生成实施方案。
- 新增 OpenSpec delta requirement，把 48/60 定义为真实生成的正文文档数量。
- 要求生成的正文文档落在 `docs_bilingual/operations_packages/` 下，并与之前的治理/登记层分离。
- 要求每个涉及执行层面的正文文档都包含 Inputs、Tools And Techniques、Outputs；中文伴随文件使用本地化等价标题。
- 要求每个正文文档都包含完整架构、全项目轻量、阶段局部轻量、模块级轻量、混合架构五种裁剪模式说明。
- 要求每一对正文文档都进入 registry。
- Stage A 和 Stage B 保持为两个串行本地 main 集成包。

## 不在范围内

- 远端发布、创建/更新/合并 GitLab MR、GitHub 同步或任何远端 ref 变更。
- Stage B 重新读取或重新抽取原始 PDF、EPUB、Markdown source library。
- 替换已经创建的白皮书、北极星、清单地图或治理/登记层运营包文档。
- 修改 LangGraph durable orchestration、launcher、`.omx/state/` 或无关治理脚本。
