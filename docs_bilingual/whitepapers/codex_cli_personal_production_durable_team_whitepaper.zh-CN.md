---
doc_id: codex_cli_personal_production_durable_team_whitepaper
lang: zh-CN
canonical: docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md
translation_of: docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md
doc_class: whitepaper
status: draft
---

# 白皮书：Codex CLI 个人开发者生产级持久化团队

## 目的

本文回答一个认知叙事问题：为什么跨多个仓库工作的个人维护者需要面向 `Codex CLI` 的个人开发者生产级持久化团队。`Codex CLI` 是原生命令行开发助手；本文是认知叙事文档，不是实施任务清单。

## 问题叙事

单个 chat session 可以辅助局部工作，但当工作需要跨越上下文丢失、重启、多会话串台、发布门、回滚和跨项目采用时，单个会话不足以作为唯一生产控制面。chat session 是一次模型对话会话。

结构性失败包括：只靠提示词的安全规则、dirty worktree、helper source truth 不清、shared runtime state 泄漏，以及 plan freeze 之前过早启动 durable team。dirty worktree 是有未提交改动的 Git 工作区；helper source truth 是辅助脚本源码真相；shared runtime state 是共享运行时状态；plan freeze 是实施前冻结计划；durable team 是持久化团队。

## 新范式

目标是一套分层的 `Codex CLI` 生产系统：

这是一套 AI 时代 value-delivery system，而不只是工具链。平台存在的目的，是帮助个人维护者在 AI 加速 research、drafting、planning 和 verification support 的同时，仍然让 value judgment、risk trade-offs、approvals、release responsibility 和 learning loops 保持可检查。

- native Codex 保持基础层；native Codex 是原生 Codex CLI 能力。
- native subagents 保持 leader-side expert bursts；native subagents 是原生专家子代理，leader-side expert bursts 是主会话按需短时调用的专家任务。
- `native_omx` 是 worker-centric durable backend lane；它只在计划冻结并且存在独立执行切片后使用。
- `langgraph` 是 graph-shaped checkpoint 和 approval lane；它只在需要 graph phase、checkpoint、approval gate 或 survivor queue 时使用。
- OpenSpec 保持仓库治理和变更控制面；OpenSpec 是 proposal、design、tasks、stable specs 和 archive 的治理工作流。
- repo-local durable state 保留在每个项目内部；repo-local durable state 是每个仓库自己的持久化状态。

## 12 层目标架构

白皮书目标不是泛泛的多 Agent 故事，而是一套受治理的 Codex CLI 平台架构：

- 12 层主干让平台从叙事一直连接到复盘学习。
- 4 个虚拟部门把平台战略/产品、工程/平台、Agent 治理、增长/知识职责分开。
- 24 个责任域、18 个横切模块、48 个核心文档定义个人开发者生产级平台的最低严肃运行面。
- 12 个受治理 AI Agent 放大执行和评审能力，但最终权威仍属于人类操作者与当前主 Codex leader 会话。
- 12 本推荐书籍提供本地管理、产品、工程、组织、安全和学习参考基础。

该清单有意小于下游一人公司经营系统清单。Codex 平台应建设开发者编排机制，而不是吸收下游客户、收入、财务、法律或运营 truth。

## PMI 交付纪律

平台叙事只有落到过程组式交付纪律中才可执行。每个发布切片都应识别输入、工具与技术、输出，然后经过启动、规划、执行、监控与控制、收尾。这让 AI 辅助交付保持可检查，并防止隐藏自动化变成审批权威。


## 核心假设

- recovery、inspection 和 rollback 比隐藏式自动化更重要。recovery 是恢复，inspection 是检查，rollback 是回滚。
- user-level helpers 只有在保持薄封装且不承载 durable truth 时才有价值。user-level helpers 是用户级辅助入口。
- 每个仓库必须保留自己的 source、OpenSpec artifacts、tests、release state 和 durable facts。source 是源码，tests 是测试，release state 是发布状态。
- local model providers 只是 advisory services，不是 approval authority 或 durable backend selector。local model providers 是本地模型服务，advisory services 是辅助建议服务。

## 非目标

- 不替代原生 `Codex CLI`。
- 不把 `oh-my-codex` 当成 Codex 替代品；`oh-my-codex` 是围绕 Codex 的工作流增强层。
- 不把 repo-local durable truth 放进 user-level virtual environment 或 helper mirror；user-level virtual environment 是用户级虚拟环境，helper mirror 是辅助脚本镜像。
- 不为只读盘点、边界冻结或单切片任务启动 durable team。
- 不混用 downstream business runtime dependencies 与 Codex CLI durable-team dependencies，除非下游项目显式拥有这些依赖。downstream business runtime dependencies 是下游业务运行依赖。

## 下游文档

- `docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.md` 是 MRD 英文主版；它定义目标项目类型、能力画像、运行归属边界和风险控制。
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` 是北极星与实施桥接计划英文主版；它把本文叙事转化为阶段目标、指标、lane 和 release slices。lane 是能力职责通道，release slices 是小版本交付切片。
- `docs_bilingual/product_lifecycle/product_business_document_lifecycle.md` 是产品与商业文档生命周期英文主版；它定义白皮书、MRD、北极星 Plan、PRD、技术设计、发布计划和复盘之间的关系。
