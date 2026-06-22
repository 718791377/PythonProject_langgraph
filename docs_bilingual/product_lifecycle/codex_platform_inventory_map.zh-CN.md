# Codex 平台清单地图

本文是本仓库目标 Codex 平台架构的简明规范清单。

## Fresh Source Evidence

本地图以 2026-06-16 fresh extraction 运行 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616`（`2026-06-15T17:33:52Z`）为证据边界。精确清单数量来自对 `Business Management/架构 1：Codex CLI 个人开发者生产级持久化团队.md` 的全文读取（source `S0030`，10,424 字符）。Business Management 来源解释运行原则；PMP 来源提供过程组与裁剪纪律。

## 规范清单

| 清单元素 | 数量 | 规范形态 |
| --- | ---: | --- |
| 主干层级 | 12 | 认知叙事、商业、市场、战略、指标、产品、技术、组织、执行、增长、运营、复盘 |
| 虚拟部门 | 4 | Strategy and Product Office；Engineering and Platform Office；Agent Governance Office；Growth and Knowledge Office |
| 责任域 | 24 | 每个部门 6 个责任域 |
| 横切模块 | 18 | 财务、运营、工程、组织、法务、安全、知识、风险、产能、Agent、数据、信任、工具链、SLA、资产、研究、渠道、退出 |
| 核心文档 | 48 | 8 个六文档族 |
| 受治理 AI Agent | 12 | Research、PM、Architect、Code、Review、Test、Security、DevOps、Data、Docs、Ops、Risk |
| 推荐书籍 | 12 | 产品、工程、操作系统、安全、交付参考书 |

## 源家族依据

| 源家族 | 在本地图中的作用 | 这里为何以它为准 |
| --- | --- | --- |
| `.omx/state/langgraph/extraction/` 下的最新架构笔记抽取 | 精确数量和命名结构 | 本地 Codex CLI 持久化团队架构笔记直接定义了 12 层、4 部门、24 域、18 模块、48 文档、12 Agent、12 书的目标形态 |
| Business Management 源 | 运行原则 | 它们支撑克制扩张、持续发现、架构边界、交付质量、团队拓扑、指标纪律、信任与可复用机制 |
| PMP 源 | 过程组运行门 | 它们提供 Initiating、Planning、Executing、Monitoring and Controlling、Closing 的运行纪律，用来驱动每一层和每个发布切片 |
| `docs_bilingual/product_lifecycle/` 既有文档 | 仓库措辞和边界对齐 | 它们把本清单接到平台构建生命周期、下游消费边界和仓库现有治理语言上 |

## 12 个主干层级

| # | 层级 | 核心问题 | 主要 owner 面 |
| ---: | --- | --- | --- |
| 0 | 认知叙事 | 为什么平台应该存在 | 愿景与 thesis |
| 1 | 商业 | 为什么值得持续维护 | 商业模式与定价 |
| 2 | 市场 | 哪类开发者和团队需要它 | 用户分层与市场地图 |
| 3 | 战略 | 什么先做，什么拒绝 | 战略与产品边界 |
| 4 | 指标 | 什么证据会改变决策 | 北极星、指标、埋点 |
| 5 | 产品 | 对外暴露哪些操作流 | PRD 与 CLI UX |
| 6 | 技术 | 如何保持安全和可演进 | 架构与 ADR |
| 7 | 组织 | 谁拥有决策和权限 | 角色图与运行节奏 |
| 8 | 执行 | 如何交付和回滚 | 交付计划与完成定义 |
| 9 | 增长 | 如何形成采用复利 | 增长模型与信任面 |
| 10 | 运营 | 如何保持支持与运行稳定 | 支持手册与变更记录 |
| 11 | 复盘 | 如何把经验沉淀下来 | 决策日志与事故复盘 |

## 4 个部门与 24 个责任域

### Strategy and Product Office

1. CEO and strategy owner
2. Chief of staff
3. Business model owner
4. Finance owner
5. Market intelligence
6. Customer research

### Engineering and Platform Office

7. Product strategy
8. PM and PRD owner
9. CLI and UX owner
10. Metrics owner
11. CTO and architect
12. Engineering manager

### Agent Governance Office

13. Code quality owner
14. DevOps owner
15. Platform and toolchain owner
16. Security owner
17. Privacy and data protection owner
18. Data governance owner

### Growth and Knowledge Office

19. Agent governance owner
20. Agent evaluation owner
21. Docs owner
22. Support owner
23. Brand and trust owner
24. Knowledge and review owner

## 18 个横切模块

| 模块组 | 模块 |
| --- | --- |
| 核心运行控制 | 财务、运营、工程管理、组织设计、法务与合规、安全 |
| 持久学习控制 | 知识管理、风险管理、个人产能、AI Agent 治理、数据治理、品牌信任 |
| 扩张与边界控制 | 工具链治理、SLA 治理、资产与 IP 治理、用户研究治理、渠道治理、退出治理 |

## 48 个核心文档

| 文档族 | 数量 | 规范文档 |
| --- | ---: | --- |
| 战略与商业 | 6 | `vision.md`、`thesis.md`、`business-model.md`、`pricing.md`、`unit-economics.md`、`strategy.md` |
| 市场与产品 | 6 | `user-segments.md`、`market-map.md`、`research-repository.md`、`product-strategy.md`、`prd.md`、`cli-ux.md` |
| 指标与数据 | 6 | `metrics.md`、`north-star.md`、`tracking-plan.md`、`data-dictionary.md`、`data-quality-checklist.md`、`experiment-log.md` |
| 工程与平台 | 6 | `architecture.md`、`adr.md`、`module-boundaries.md`、`tech-stack.md`、`delivery-plan.md`、`observability.md` |
| 安全与风险 | 6 | `security-policy.md`、`access-control.md`、`privacy-policy.md`、`incident-response.md`、`risk-register.md`、`backup-restore.md` |
| Agent 治理 | 6 | `agent-role-map.md`、`agent-permissions.md`、`agent-governance.md`、`human-review-checklist.md`、`agent-evaluation.md`、`agent-failure-modes.md` |
| 增长与运营 | 6 | `growth-model.md`、`docs-plan.md`、`support-playbook.md`、`faq.md`、`trust-page.md`、`changelog.md` |
| 复盘与知识 | 6 | `decision-log.md`、`weekly-review.md`、`monthly-review.md`、`postmortem.md`、`learning-log.md`、`template-library.md` |

## 12 个受治理 AI Agent

| Agent | 主通道 | 人工门 |
| --- | --- | --- |
| Research Agent | 研究与证据整理 | 战略解释 |
| PM Agent | PRD 与验收草稿 | 范围与优先级 |
| Architect Agent | ADR 与边界草稿 | 最终架构决策 |
| Code Agent | 实现与重构 | 合并批准 |
| Review Agent | 评审结论与发布预警 | 是否接受发布 |
| Test Agent | 测试编写与回归检查 | 删除测试与发布签字 |
| Security Agent | 安全审查与依赖检查 | 权限与生产变更 |
| DevOps Agent | CI、部署、可观测草稿 | 生产部署 |
| Data Agent | 指标分析与看板草稿 | 指标定义调整 |
| Docs Agent | README、FAQ、生命周期文档 | 对外承诺 |
| Ops Agent | 分流、总结、运营复盘 | 面向用户的回复 |
| Risk Agent | 风险、合规、license 审查 | 法务与政策发布 |

## 12 本推荐书籍

1. Scaling People
2. Working Backwards
3. High Output Management
4. INSPIRED
5. Product Operations
6. Team Topologies
7. Accelerate
8. Shape Up
9. Lean Analytics
10. Designing Data-Intensive Applications
11. Secure by Design
12. The Staff Engineer's Path


## 分层级输入、工具与技术、输出

12 个主干层级都可以轻量或完整运行，但涉及执行的工作必须能写成“输入、工具与技术、输出”。

| 层级组 | 输入 | 工具与技术 | 输出 |
| --- | --- | --- | --- |
| 0-2 叙事、商业、市场 | 用户问题、来源证据、stakeholder 信号、市场/采用假设 | 战略诊断、PR/FAQ、访谈综合、定位、启动门 | 白皮书更新、商业边界、市场/采用假设、初始风险 |
| 3-5 战略、指标、产品 | 北极星、OKR、生命周期裁剪决定、机会证据 | 指导方针设计、OMTM/护栏设计、产品发现、规划门 | 战略计划、指标契约、PRD 或发布切片 brief、验收标准 |
| 6-8 技术、组织、执行 | 架构约束、角色/Agent map、实施计划、worktree ownership | 架构审查、威胁/风险审查、OpenSpec、subagent/durable-team 阈值检查、执行门 | 技术设计、责任矩阵、已提交变更、验证证据 |
| 9-11 增长、运营、复盘 | 发布证据、使用/采用信号、事故、经验教训 | 监控与控制、项目组合 review、PMO 式治理服务、收尾门 | 发布说明、运行手册、复盘、归档与下一周期决定 |

## 过程组运行门

| 过程组 | 输入 | 工具与技术 | 输出 |
| --- | --- | --- | --- |
| Initiating | 候选层级、文档族、模块、Agent 面、价值假设、范围边界 | 目标清单映射、owner 识别、非目标检查、durable-state 边界检查 | 目的、价值假设、owner、范围边界、初始风险 |
| Planning | 启动输出、依赖、验收标准、风险画像、人机边界 | I/T/O planning、release slicing、验证设计、回滚设计、角色边界评审 | 验收标准、依赖图、风险响应、验证路径、人机边界 |
| Executing | 已批准切片、来源证据、模板、worktree 状态、角色所有权 | 受控起草或实现、评审、测试、文档更新、满足条件时的 expert/durable-lane handoff | 草稿制品、受控改动集、验证工作、changed-path 证据 |
| Monitoring and Controlling | 活跃改动集、指标、问题、评审结论、gate 输出 | local gate、OpenSpec guard、diff review、问题分流、变更控制、回滚准备检查 | 指标、问题日志、评审结论、本地 gate 证据、回滚准备 |
| Closing | 已验收工件、验证证据、归档候选、经验教训 | 归档/同步、发布说明更新、复盘、下一周期分流 | 最终文档或政策、归档记录、经验教训、下一周期输入 |

## 使用规则

当平台变更需要说明它落在哪个目标架构位置时，使用本地图。一个非平凡切片至少应点名一个受影响层级、一个部门、一个责任域、一个模块组、一个核心文档族，以及任何发生变化的 Agent 边界。
