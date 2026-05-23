# 一人公司清单地图

本文是下游一人公司操作系统目标的简明规范清单。

## 规范清单

| 清单元素 | 数量 | 规范形态 |
| --- | ---: | --- |
| 主干层级 | 12 | 认知叙事、商业、市场、战略、指标、产品、技术、组织、执行、增长、运营、复盘 |
| 虚拟部门 | 5 | Strategy Office；Product and Market Office；Revenue and Growth Office；Operations Office；Governance Office |
| 责任域 | 30 | 每个部门 6 个责任域 |
| 横切模块 | 20 | 财务、运营、工程、组织、法务、安全、知识、风险、产能、Agent、数据、信任、工具链、SLA、资产、研究、渠道、退出、供应商、税务 |
| 核心文档 | 60 | 10 个文档族 |
| 受治理 AI Agent | 15 | Strategy、Research、Product、UX and Copy、Engineering、QA、Data、Growth、Sales、Customer Success、Support、Finance、Legal and Risk、Knowledge、Chief of Staff |
| 推荐书籍 | 15 | 战略、产品、增长、操作系统、一人公司参考书 |
| 最小启动文档 | 12 | 启动时最小运行集合 |

## 源家族依据

| 源家族 | 在本地图中的作用 | 这里为何以它为准 |
| --- | --- | --- |
| `.omx/state/langgraph/extraction/` 下的最新架构笔记抽取 | 精确数量和命名结构 | 本地一人公司架构笔记直接定义了 12 层、5 部门、30 域、20 模块、60 文档、15 Agent、15 书、12 启动文档的目标形态 |
| Business Management 源 | 运行原则 | 它们支撑一人公司范围克制、持续发现、定价清晰、牵引闭环、运行节奏、流程化和有意识地系统化 |
| PMP 源 | 过程组运行门 | 它们提供统一 gate 模型，用来驱动商业工作的规划、执行、控制和收尾 |
| `docs_bilingual/product_lifecycle/` 既有文档 | 平台到项目的边界对齐 | 它们保证本目标被定位为下游业务架构，而不是平台仓库的持久真相 |

## 12 个主干层级

| # | 层级 | 核心问题 | 主要 owner 面 |
| ---: | --- | --- | --- |
| 0 | 认知叙事 | 为什么公司应该存在 | 公司 thesis 与愿景 |
| 1 | 商业 | 如何赚钱并保持可持续 | 商业模式与财务模型 |
| 2 | 市场 | 哪些用户和细分最重要 | 市场地图与用户分层 |
| 3 | 战略 | 狭窄胜利条件是什么 | 战略与年度计划 |
| 4 | 指标 | 什么证据决定下一步 | 北极星、漏斗、埋点 |
| 5 | 产品 | 到底卖什么、交付什么 | offer、PRD、服务蓝图 |
| 6 | 技术 | 哪些自动化和系统支撑交付 | 技术栈与自动化地图 |
| 7 | 组织 | 创始人、Agent、合作方如何分工 | 角色图与 Agent 治理 |
| 8 | 执行 | 当前如何把事做出来 | 季度计划与交付计划 |
| 9 | 增长 | 需求如何形成复利 | 增长模型与渠道地图 |
| 10 | 运营 | 交付、支持、续费如何保持稳定 | 运营手册与客户成功 |
| 11 | 复盘 | 学习如何更新公司系统 | 月复盘与学习日志 |

## 5 个部门与 30 个责任域

### Strategy Office

1. Founder and CEO
2. Chief of staff
3. Business model owner
4. Finance owner
5. Risk owner
6. Personal operating-system owner

### Product and Market Office

7. Market intelligence
8. Customer research
9. Positioning owner
10. Product strategy owner
11. Offer owner
12. PRD and service-design owner

### Revenue and Growth Office

13. Analytics owner
14. Growth owner
15. Sales owner
16. Pricing owner
17. Content owner
18. Brand and trust owner

### Operations Office

19. Partnerships owner
20. Customer success owner
21. Support owner
22. Delivery owner
23. Community owner
24. Knowledge owner

### Governance Office

25. Automation owner
26. Security and privacy owner
27. Legal and compliance owner
28. Data governance owner
29. Asset and IP owner
30. Agent governance owner

## 20 个横切模块

| 模块组 | 模块 |
| --- | --- |
| 核心商业控制 | 财务、运营、工程管理、组织设计、法务与合规、安全、知识管理 |
| 持久执行控制 | 风险管理、个人产能、AI Agent 治理、数据治理、品牌信任、工具链治理、SLA 治理 |
| 扩张与边界控制 | 资产与 IP 治理、用户研究治理、渠道治理、退出治理、供应商治理、税务与行政治理 |

## 60 个核心文档

| 文档族 | 数量 | 规范文档 |
| --- | ---: | --- |
| 公司战略 | 6 | `company-thesis.md`、`vision.md`、`strategy.md`、`annual-plan.md`、`quarterly-plan.md`、`decision-log.md` |
| 商业与财务 | 6 | `business-model.md`、`offer.md`、`pricing.md`、`unit-economics.md`、`finance-model.md`、`cashflow.md` |
| 市场与用户 | 6 | `market-map.md`、`user-segments.md`、`competitor-analysis.md`、`alternative-solutions.md`、`research-repository.md`、`interview-guide.md` |
| 产品与服务 | 6 | `product-strategy.md`、`prd.md`、`service-blueprint.md`、`onboarding.md`、`customer-journey.md`、`roadmap.md` |
| 指标与数据 | 6 | `metrics.yaml`、`north-star.md`、`funnel-dashboard.md`、`tracking-plan.md`、`data-dictionary.md`、`experiment-log.md` |
| 增长与销售 | 6 | `growth-model.md`、`channel-map.md`、`sales-playbook.md`、`landing-page.md`、`email-sequences.md`、`content-calendar.md` |
| 运营与客户成功 | 6 | `ops-playbook.md`、`customer-success-playbook.md`、`support-policy.md`、`faq.md`、`refund-policy.md`、`feedback-triage.md` |
| 技术与自动化 | 6 | `tech-stack.md`、`automation-map.md`、`tool-stack.md`、`vendor-register.md`、`api-dependency-map.md`、`backup-restore.md` |
| 治理与风险 | 6 | `legal-checklist.md`、`terms-of-service.md`、`privacy-policy.md`、`contract-template.md`、`risk-register.md`、`compliance-checklist.md` |
| Agent 与知识 | 6 | `agent-governance.md`、`agent-role-map.md`、`agent-permissions.md`、`human-review-checklist.md`、`monthly-review.md`、`learning-log.md` |

## 15 个受治理 AI Agent

| Agent | 主通道 | 人工门 |
| --- | --- | --- |
| Strategy Agent | 机会分析与战略草稿 | 最终战略取舍 |
| Research Agent | 用户、市场、竞品研究 | 洞察解释 |
| Product Agent | PRD、路线图、服务设计草稿 | 范围与对外承诺 |
| UX and Copy Agent | 落地页、引导、文案草稿 | 对外发布 |
| Engineering Agent | 产品与自动化实现 | 合并与发布批准 |
| QA Agent | 测试与验收审查 | 发布签字 |
| Data Agent | 指标分析与实验复盘 | 指标定义变更 |
| Growth Agent | 渠道测试与内容实验 | 带预算投放启动 |
| Sales Agent | 提案与销售材料草稿 | 定价与承诺 |
| Customer Success Agent | 续费、案例、生命周期支持草稿 | 客户承诺 |
| Support Agent | FAQ、回复草稿、问题分流 | 退款与投诉决策 |
| Finance Agent | 成本、预算、现金流复盘 | 付款与税务决策 |
| Legal and Risk Agent | 条款、license、风险草稿 | 合同与政策发布 |
| Knowledge Agent | SOP、复盘、知识库更新 | 持久决策归档 |
| Chief of Staff Agent | 周报、月报、节奏总结 | 优先级重置 |

## 15 本推荐书籍

1. Scaling People
2. Working Backwards
3. High Output Management
4. INSPIRED
5. Product Operations
6. Measure What Matters
7. Lean Analytics
8. The Lean Startup
9. Obviously Awesome
10. Traction
11. Deploy Empathy
12. Shape Up
13. Team Topologies
14. Company of One
15. The E-Myth Revisited

## 12 个最小启动文档

1. `company-thesis.md` - 说明公司为什么存在，以及正在验证什么核心信念。
2. `business-model.md` - 定义公司如何创造、交付并获取价值。
3. `offer.md` - 描述第一个付费或已验证 offer。
4. `pricing.md` - 记录定价逻辑、套餐和折扣边界。
5. `user-segments.md` - 识别第一批目标用户和非目标用户。
6. `growth-model.md` - 解释第一条需求与采用增长循环。
7. `finance-model.md` - 跟踪成本、现金流假设和 runway 约束。
8. `ops-playbook.md` - 定义交付、支持和运行节奏。
9. `metrics.yaml` - 提供机器可读指标契约。
10. `risk-register.md` - 记录风险、触发器、响应和 owner。
11. `agent-governance.md` - 定义 AI Agent 角色、权限和人工评审。
12. `monthly-review.md` - 沉淀学习、决策和下一周期更新。

## 过程组运行门

| 过程组 | 门问题 | 本清单要求的输出 |
| --- | --- | --- |
| Initiating | 某条业务线、文档族或 Agent 面是否应该存在 | 客户问题、价值理由、owner、范围边界 |
| Planning | 本周期应如何运行 | 成功标准、依赖、现金与时间约束、风险响应、人机边界 |
| Executing | 当前在交付或运营什么 | 草稿制品、活跃计划、面向客户的工作、验证证据 |
| Monitoring and Controlling | 公司系统是否仍然健康 | 指标复盘、问题日志、现金与支持检查、客户反馈、回滚或停止触发器 |
| Closing | 周期结束后什么要变成持久资产 | 更新后的政策或手册、复盘制品、归档决策、下一周期输入 |

## 使用规则

当下游业务项目需要一个规范操作系统目标时，使用本地图。先从 12 个最小启动文档开始，只有在客户证据、收入暴露、交付复杂度或治理风险要求更深覆盖时，再扩展到 60 文档系统。
