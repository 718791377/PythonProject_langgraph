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

## 为什么白皮书与研究稿分开

同一主题保留两份文档是有意设计，因为它们承担不同职责。

- 白皮书：解释平台为什么需要这个方向、提出什么范式变化、Codex 平台应保持什么边界。
- 研究稿：解释哪些生产级能力是必需的、哪些结论来自官方来源或工程推导、为什么持久化工作流系统要求更严格的运行模型。

因此，白皮书保持更短、更面向方向决策；研究稿保持证据更重、更面向治理。

## 合并规则

- 只要两份文档服务不同读者、评审路径或生命周期角色，就保持分开。
- 当变更同时影响平台叙事和生产级能力判据时，两份文档都要更新。
- 不要只因为主题重叠就合并。
- 只有当其中一份文件变成没有独立功能的薄重复文件时，才考虑合并；当前未达到该阈值。

1. 白皮书可以总结研究结论，但不得吸收完整能力目录。
2. 研究稿可以支撑或修正白皮书，但不得替代平台叙事。
3. Implementation plan 和生命周期文档在同时需要“为什么要做”和“为什么必须严格”两类证据时，应同时引用两份文件。

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

## 10 层到 12 层桥接

支撑研究稿使用 10 层 runtime/governance 分解，因为它研究生产级持久化团队在执行时必须具备哪些能力。本文使用仓库的 12 层产品/商业生命周期主干，因为本仓库还要治理产品、市场、发布、运营和复盘行为。

- 研究稿第 1-3 层主要落到生命周期的技术、组织和执行层。
- 研究稿第 4-6 层根据关注点不同，落到技术、指标和运营层：存储、检索质量和运行策略分别需要不同 owner。
- 研究稿第 7-10 层跨越技术、组织、执行、运营和复盘层，因为质量、评测、安全和控制中心设计都需要生命周期 owner。
- 12 层生命周期还增加了研究稿不直接承担的四个主干：认知叙事、商业、市场和增长。

这正是两份文件应保持分开的原因：研究稿拆解 runtime 生产能力，白皮书把这些能力放入更大的平台生命周期。参见 `docs_bilingual/governance/solo_maintainable_production_persistent_team_research.zh-CN.md` 和 `docs_bilingual/product_lifecycle/product_business_document_lifecycle.zh-CN.md`。

## 12-layer target architecture

- 12 层主干让平台从叙事一直连接到复盘学习。
- 4 个虚拟部门把平台战略/产品、工程/平台、Agent 治理、增长/知识职责分开。
- 24 个责任域、18 个横切模块、48 个核心文档定义个人开发者生产级平台的最低严肃运行面。
- 12 个受治理 AI Agent 放大执行和评审能力，但最终权威仍属于人类操作者与当前主 Codex leader 会话。
- 12 本推荐书籍提供本地管理、产品、工程、组织、安全和学习参考基础。

该清单有意小于下游一人公司经营系统清单。Codex 平台应建设开发者编排机制，而不是吸收下游客户、收入、财务、法律或运营 truth。数量权威见 `docs_bilingual/product_lifecycle/codex_platform_inventory_map.zh-CN.md`；下游一人公司对照权威见 `docs_bilingual/product_lifecycle/one_person_company_inventory_map.zh-CN.md`。

## PMI 交付纪律

平台叙事只有落到过程组式交付纪律中才可执行。每个发布切片都应识别输入、工具与技术、输出，然后经过启动、规划、执行、监控与控制、收尾。这让 AI 辅助交付保持可检查，并防止隐藏自动化变成审批权威。显式参考映射见 `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.zh-CN.md`：PMBOK 第8版是价值交付和裁剪的主要叠加层，PMBOK 第7版和第6版是补充，Process Groups 提供交付门，Agile Practice Guide 提供适应式/混合交付，项目集管理提供多倡议对齐，项目组合管理提供价值/容量平衡，PMO 实践指南提供治理服务模式。

## 架构裁剪规则

裁剪有五种明确结果。凡是影响可复用编排、信任、durable state、release safety 或跨项目采用的受影响范围，都使用完整架构。只有私有、可逆、低风险，并且没有外部用户、金钱、敏感数据、共享 runtime 或发布承诺时，才允许整个项目轻量。当较大受治理项目中的某个低风险阶段可以简化时，使用阶段局部轻量。当单个有边界模块可逆且不破坏完整项目边界时，使用模块级轻量。当发现仍不确定，但最终交付可能影响生产、用户、信任、收入、合规、runtime behavior 或 release safety 时，使用混合方式。详细规则位于 `docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.zh-CN.md`。


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

## Cross-links

- `docs_bilingual/governance/solo_maintainable_production_persistent_team_research.zh-CN.md` 是本文的详细能力与证据伴随文档。
- `docs_bilingual/product_lifecycle/product_business_document_lifecycle.zh-CN.md` 定义本仓库使用的 12 层文档栈。
- `docs_bilingual/product_lifecycle/codex_platform_inventory_map.zh-CN.md` 与 `docs_bilingual/product_lifecycle/one_person_company_inventory_map.zh-CN.md` 定义两套数量权威。
- `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.zh-CN.md` 与 `docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.zh-CN.md` 定义 PMI 叠加层与裁剪权威。
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` 把本文方向转换为分阶段平台方案。

## Downstream documents

- `docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.zh-CN.md` 是 MRD；它定义目标项目类型、能力画像、运行归属边界和风险控制。
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` 是北极星与实施桥接方案；它把本文叙事转换成阶段目标、指标、lane 和发布切片。
- `docs_bilingual/product_lifecycle/product_business_document_lifecycle.zh-CN.md` 是生命周期参考；它定义白皮书、MRD、北极星计划、PRD、技术设计、发布计划和复盘之间的关系。
