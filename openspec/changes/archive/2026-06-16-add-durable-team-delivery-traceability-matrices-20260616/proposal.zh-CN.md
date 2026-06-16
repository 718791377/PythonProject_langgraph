## 为什么

持久化团队文档族已经有新的本地 fresh reading 运行，但已提交语料仍缺少明确的交付矩阵、来源追踪索引和过程组契约。没有这些证明面，冷启动维护者虽然能看到白皮书、研究稿、生命周期、实施方案、playbook 与 OpenSpec 文档已经刷新，但不能快速判断每个文件满足哪条用户要求、哪些证据已经提交、以及什么时候必须使用“输入 / 工具与技术 / 输出”。

本变更继续保持白皮书和研究稿分离，只增加桥接与证明文档，让 10 层运行时/治理能力核心可以清晰落到 12 层产品/商业生命周期规划框架中。

## 变更内容

- 在 `docs_bilingual/implementation_plans/` 下新增持久化团队交付矩阵。
- 在 `docs_bilingual/product_lifecycle/` 下新增持久化团队来源追踪索引。
- 在 `docs_bilingual/product_lifecycle/` 下新增持久化团队过程组契约。
- 将活跃持久化团队语料中的上一轮 20260614 证据引用刷新为 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616`，生成时间 `2026-06-15T17:33:52Z`。
- 更新 docs registry 与 OpenSpec requirement，使这些证明面受治理并可被冷启动维护者发现。

## 非目标

- 不物理合并白皮书与研究稿。
- 不声称 durable 或 persistent team runtime 已经实现或正在运行。
- 不提交 raw extraction text、逐单元抽取流或本地 cache/log。
- 不改变 launcher、subagent routing、`native_omx`、LangGraph runtime state、model provider 或远程发布状态。

## 治理字段

- `impact_scope`：面向 durable-team 文档族的 docs-only 证明面与稳定规格同步。
- `explicit_non_goals`：不启动 runtime、不远程发布、不提交原始来源文本、不合并白皮书与研究稿。
- `rollout_sequence`：创建 OpenSpec artifacts；新增证明面；刷新活跃语料引用；更新稳定与增量规格；验证；归档；提交有界包。
- `rollback_plan`：回滚本分支提交，或从 local `main` 恢复被触及的文档与规格文件。
- `validation_path`：OpenSpec strict validation、双语文档对检查、implementation-plan rules、name clarity、mojibake guard、precommit update/archive review、local gate，以及 local MR review。
