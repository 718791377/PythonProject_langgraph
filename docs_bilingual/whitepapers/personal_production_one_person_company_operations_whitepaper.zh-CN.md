---
doc_id: personal_production_one_person_company_operations_whitepaper
lang: zh-CN
canonical: docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.md
translation_of: docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.md
doc_class: whitepaper
status: draft
---

# 白皮书：个人级生产级一人公司运营

## 目的

本文解释为什么个人经营者需要一套个人级生产级一人公司运营系统，以及这套系统如何在保持轻量的同时避免把每个小动作都变成大型企业官僚流程。

本文是下游业务 operating-system 白皮书。它不替代 Codex CLI 个人开发者生产级持久化团队白皮书，也不把下游客户、收入、财务、法务、支持或运营事实迁入本平台仓库。

## 本轮 Fresh Source Evidence

本轮刷新基于新的本地抽取运行 `one-person-company-pmi-refresh-stageb-20260619`，生成时间为 `2026-06-18T18:37:58Z`。该运行按 PDF 每页、EPUB spine item、Markdown 全文读取忽略态本地源根 `Business Management/` 与 `PMP/`，并把本地证据写入 `.omx/state/langgraph/extraction/business_pmp_20260619/`。

该运行覆盖 54 个来源：31 个 Business Management 来源和 23 个 PMP 来源。格式覆盖为 31 个 PDF / 9,280 页、9 个 EPUB / 362 个 spine item、14 个 Markdown 全文文件。全部 54 个来源均以 `ok` 状态完成，共 9,656 个读取单元和 18,492,044 个抽取字符。另有 `one-person-company-pmi-refresh-stageb-product-lifecycle-20260619` 对 `docs_bilingual/product_lifecycle/` 下 26 个 Markdown 文档进行全文读取，共 310,349 个字符，全部 `ok`。

被跟踪文档只能引用聚合数量、来源家族名称和仓库特定综合结论。原始抽取文本只作为忽略态本地证据，不得复制进被跟踪文档。

## 为什么需要这套运营系统

一人公司在外部看起来很小，但仍然可能承担严肃的运营复杂度：客户发现、定位、定价、交付、支持、现金流、风险、自动化、法律边界和学习循环。目标不是模仿大公司，而是在 AI Agent 与自动化提高吞吐量时，让个人经营者仍能做出清晰、可检查、可复盘的判断。

因此，这套 operating system 有三条设计约束：

- 保持最小可运行公司面可见。
- 只扩展被客户、收入、信任、合规、支持、交付或自动化风险触达的层级。
- 即使受治理 AI Agent 参与起草、检查、分析或执行，最终责任仍属于人类 owner。

## 规范清单

目标清单由 `one_person_company_inventory_map.zh-CN.md` 固定：

| 元素 | 数量 | 含义 |
| --- | ---: | --- |
| 主干层级 | 12 | 认知叙事、商业、市场、战略、指标、产品、技术、组织、执行、增长、运营、复盘 |
| 虚拟部门 | 5 | Strategy Office、Product and Market Office、Revenue and Growth Office、Operations Office、Governance Office |
| 责任域 | 30 | 每个虚拟部门 6 个责任域 |
| 横切模块 | 20 | 财务、运营、工程、组织、法务、安全、知识、风险、产能、Agent、数据、信任、工具链、SLA、资产、研究、渠道、退出、供应商、税务 |
| 核心文档 | 60 | 10 个文档族，每族 6 份文档 |
| 受治理 AI Agent | 15 | 角色有边界、带人工评审门的辅助 Agent |
| 推荐书籍 | 15 | 战略、产品、增长、运营、组织和一人公司参考基础 |
| 最小启动文档 | 12 | 启动真实经营循环的最小集合 |

## 专属北极星

一人公司专属北极星位于 `docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.zh-CN.md`。它的主指标是“已验证运营循环吞吐量”：在一个评审周期内，从客户或运营证据启动，经过必要人工与治理门，产出已交付或已验证业务输出，并把学习回流到下一周期的业务循环数量。

该北极星不是 Codex 持久化团队平台北极星。平台北极星度量编排能力；一人公司北极星度量下游业务学习与交付。

## 12 层运营模型

每一层都有主问题和 I/T/O 契约。I/T/O 指输入、工具与技术、输出。

| # | 层级 | 主问题 | 输入 | 工具与技术 | 输出 |
| ---: | --- | --- | --- | --- | --- |
| 0 | 认知叙事 | 为什么公司应该存在？ | 创始人信念、客户痛点、个人约束、市场信号 | thesis 写作、PR/FAQ 思考、战略诊断、停止条件 framing | `thesis.md`、愿景陈述、明确非目标 |
| 1 | 商业 | 公司如何赚钱并保持可持续？ | offer 假设、成本基础、定价信号、现金 runway | 商业模式映射、单位经济复核、现金流建模、情景检查 | `business-model.md`、`finance-model.md`、`cashflow.md` |
| 2 | 市场 | 哪些用户和细分最先重要？ | 用户访谈、替代方案、渠道观察、竞品证据 | 分层、定位、竞品分析、访谈综合 | `market-map.md`、`user-segments.md`、研究仓库 |
| 3 | 战略 | 狭窄胜利条件是什么？ | 叙事、商业模式、市场证据、产能约束 | 好战略诊断、年度/季度规划、取舍复核、决策记录 | `strategy.md`、`annual-plan.md`、`quarterly-plan.md` |
| 4 | 指标 | 什么证据会改变下一步？ | 北极星候选、漏斗事件、财务限制、支持信号 | OMTM 选择、OKR review、tracking plan 设计、护栏定义 | `north-star.md`、`metrics.md`、漏斗 dashboard、实验日志 |
| 5 | 产品 | 到底卖什么、交付什么？ | 客户任务、offer 承诺、约束、验收证据 | 产品发现、PRD 写作、服务蓝图设计、MVP 切片 | `offer.md`、`prd.md`、服务蓝图、路线图 |
| 6 | 技术 | 哪些系统与自动化支撑交付？ | 产品承诺、数据需求、安全约束、支持负载 | 架构审查、自动化映射、供应商复核、备份恢复规划 | `tech-stack.md`、`automation-map.md`、依赖地图、恢复说明 |
| 7 | 组织 | 创始人、Agent、合作方如何分工？ | 角色负载、Agent 候选、供应商边界、评审需求 | 责任映射、Agent 治理设计、权限复核、人工评审门 | 角色图、`agent-governance.md`、权限、评审清单 |
| 8 | 执行 | 当前工作如何交付？ | 已批准周期计划、容量、风险、依赖、验证计划 | 过程组规划、工作切片、Kanban 或周期 planning、验收复核 | 交付计划、已提交工作、验证证据、发布候选 |
| 9 | 增长 | 需求如何形成复利？ | 细分证据、渠道信号、内容资产、转化数据 | Traction 渠道测试、增长循环设计、销售手册迭代、定价复核 | `growth-model.md`、渠道地图、销售手册、内容日历 |
| 10 | 运营 | 交付、支持、留存如何保持稳定？ | 客户承诺、支持工单、履约约束、SLA 需求 | 运营手册设计、客户成功复核、支持分流、退款政策复核 | `ops-playbook.md`、客户成功手册、支持政策、FAQ |
| 11 | 复盘 | 学习如何更新公司系统？ | 指标、决策、事故、客户反馈、财务/支持证据 | 月复盘、决策归档、经验教训综合、下一周期优先级排序 | `monthly-review.md`、学习日志、更新后的政策、下一周期输入 |

## 5 个虚拟部门与 30 个责任域

虚拟部门不是 headcount，而是个人经营者的责任视角。

| 部门 | 六个责任域 |
| --- | --- |
| Strategy Office | Founder and CEO；Chief of Staff；business model owner；finance owner；risk owner；personal operating-system owner |
| Product and Market Office | Market intelligence；customer research；positioning owner；product strategy owner；offer owner；PRD and service-design owner |
| Revenue and Growth Office | Analytics owner；growth owner；sales owner；pricing owner；content owner；brand and trust owner |
| Operations Office | Partnerships owner；customer success owner；support owner；delivery owner；community owner；knowledge owner |
| Governance Office | Automation owner；security and privacy owner；legal and compliance owner；data-governance owner；asset and IP owner；agent-governance owner |

## 20 个横切模块

横切模块用于防止局部决策变成隐藏风险。只有受影响工作确实需要时才激活。

| 模块组 | 模块 |
| --- | --- |
| 核心商业控制 | 财务、运营、工程管理、组织设计、法务合规、安全、知识管理 |
| 持久执行控制 | 风险管理、个人产能、AI Agent 治理、数据治理、品牌信任、工具链治理、SLA 治理 |
| 边界与扩展控制 | 资产/IP 治理、用户研究治理、渠道治理、退出治理、供应商治理、税务/行政治理 |

## 60 个核心文档

完整文档系统包含 10 个文档族。一人公司先从最小启动集开始，只有证据证明需要更深覆盖时才扩展。

| 文档族 | 文档 |
| --- | --- |
| 公司战略 | `thesis.md`、`vision.md`、`strategy.md`、`annual-plan.md`、`quarterly-plan.md`、`decision-log.md` |
| 商业与财务 | `business-model.md`、`offer.md`、`pricing.md`、`unit-economics.md`、`finance-model.md`、`cashflow.md` |
| 市场与用户 | `market-map.md`、`user-segments.md`、`competitor-analysis.md`、`alternative-solutions.md`、`research-repository.md`、`interview-guide.md` |
| 产品与服务 | `product-strategy.md`、`prd.md`、`service-blueprint.md`、`onboarding.md`、`customer-journey.md`、`roadmap.md` |
| 指标与数据 | `metrics.md`、`north-star.md`、`funnel-dashboard.md`、`tracking-plan.md`、`data-dictionary.md`、`experiment-log.md` |
| 增长与销售 | `growth-model.md`、`channel-map.md`、`sales-playbook.md`、`landing-page.md`、`email-sequences.md`、`content-calendar.md` |
| 运营与客户成功 | `ops-playbook.md`、`customer-success-playbook.md`、`support-playbook.md`、`faq.md`、`refund-policy.md`、`feedback-triage.md` |
| 技术与自动化 | `tech-stack.md`、`automation-map.md`、`tool-stack.md`、`vendor-register.md`、`api-dependency-map.md`、`backup-restore.md` |
| 治理与风险 | `legal-checklist.md`、`terms-of-service.md`、`privacy-policy.md`、`contract-template.md`、`risk-register.md`、`compliance-checklist.md` |
| Agent 与知识 | `agent-governance.md`、`agent-role-map.md`、`agent-permissions.md`、`human-review-checklist.md`、`monthly-review.md`、`learning-log.md` |

## 12 个最小启动文档

启动集合刻意小于完整系统：

1. `thesis.md` - 说明公司为什么存在，以及正在验证什么信念。
2. `business-model.md` - 解释公司如何创造、交付并获取价值。
3. `offer.md` - 定义第一个付费或已验证承诺。
4. `pricing.md` - 记录套餐、价格逻辑和折扣边界。
5. `user-segments.md` - 识别第一批目标用户和明确非目标用户。
6. `growth-model.md` - 解释第一条需求与采用循环。
7. `finance-model.md` - 跟踪成本、runway、现金流和可持续假设。
8. `ops-playbook.md` - 定义履约、支持和运行节奏。
9. `metrics.md` - 保持机器可读指标契约。
10. `risk-register.md` - 记录风险、触发器、响应和 owner。
11. `agent-governance.md` - 定义 AI Agent 角色、权限和人工评审。
12. `monthly-review.md` - 沉淀学习、决策和下一周期更新。

这些文档足以说明公司为什么存在、卖什么、服务谁、如何增长、如何保持财务存活、如何交付、如何衡量进展、控制哪些风险、如何治理 AI Agent，以及如何把学习更新回系统。

## 15 个受治理 AI Agent

Agent 扩展的是产能，不是最终权威。

| Agent | 主通道 | 人工评审门 |
| --- | --- | --- |
| Strategy Agent | 机会分析与战略草稿 | 最终战略取舍 |
| Research Agent | 用户、市场和竞品研究 | 洞察解释 |
| Product Agent | PRD、路线图和服务设计草稿 | 范围和对外承诺 |
| UX and Copy Agent | 落地页、引导和文案草稿 | 对外发布 |
| Engineering Agent | 产品与自动化实现支持 | 合并与发布批准 |
| QA Agent | 测试与验收审查 | 发布签字 |
| Data Agent | 指标分析和实验复盘 | 指标定义变更 |
| Growth Agent | 渠道测试和内容实验 | 付费或带预算启动 |
| Sales Agent | 提案和销售材料草稿 | 定价和承诺 |
| Customer Success Agent | 续费、案例和生命周期支持草稿 | 客户承诺 |
| Support Agent | FAQ、回复草稿和问题分流 | 退款与投诉决策 |
| Finance Agent | 成本、预算和现金流复核 | 付款与税务决策 |
| Legal and Risk Agent | 条款、license 和风险草稿 | 合同与政策发布 |
| Knowledge Agent | SOP、复盘和知识库更新 | 持久决策归档 |
| Chief of Staff Agent | 周报、月报和节奏复核 | 优先级重置 |

## 推荐阅读集

推荐书籍是实用参考基础，不是认证清单：

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

## PMI 过程组式运行模型

当工作影响客户、收入、信任、支持、合规、交付承诺、发布安全或受治理自动化时，执行层应采用过程组式写法。

| 过程组 | 输入 | 工具与技术 | 输出 |
| --- | --- | --- | --- |
| 启动 | 客户问题、价值理由、候选业务线、活跃文档族、Agent 面、现金与时间边界 | 客户证据复核、owner 映射、收入和风险 framing、范围边界、停止条件 framing | 问题陈述、价值理由、责任 owner、范围边界、初始风险或停止条件 |
| 规划 | 启动输出、容量、依赖、现金/时间限制、支持负载、人机边界 | 周期 planning、offer 和 segment review、风险响应规划、验证规划、budget/runway check、人工评审设计 | 成功标准、依赖图、现金/时间约束、风险响应、验证计划、人工评审门 |
| 执行 | 已批准周期计划、客户证据、运营模板、Agent 规则、验证计划 | 交付、销售、支持、访谈、测量、受控 AI 起草与检查 | 草稿或已交付制品、活跃客户工作、验证证据、问题日志 |
| 监控与控制 | 指标、问题日志、现金/支持信号、客户反馈、风险触发器 | 指标复盘、现金检查、支持复核、反馈综合、变更控制、回滚或停止决策 | 指标复盘、更新后的问题日志、现金/支持检查、客户反馈综合、回滚/停止触发器 |
| 收尾 | 周期输出、决策、财务/支持证据、经验教训 | 月复盘、政策或手册更新、归档、下一周期优先级排序 | 更新后的政策或手册、复盘制品、归档决策、下一周期输入 |

## 裁剪规则

一人公司不应默认启动完整 60 文档系统。裁剪有五种明确结果：

| 裁剪结果 | 适用场景 | 必需最小面 |
| --- | --- | --- |
| 受影响范围使用完整架构 | 新产品、重大业务转向、用户可见发布、支付、合规、敏感数据、信任影响、重复交付、支持义务、外部承诺或广泛 Agent 自动化 | 所有受影响层级都显示 I/T/O、风险、owner、验证和复盘路径 |
| 整个项目轻量 | 私有、可逆、低风险，且没有外部用户、金钱、敏感数据、支持承诺、共享 runtime 或发布承诺 | 最小启动文档加明确停止条件 |
| 阶段局部轻量 | 较大受治理项目中的 discovery、原型、访谈或内容探索阶段风险较低 | 轻量化只留在该阶段；在触达客户、收入、信任或发布影响前扩展 |
| 模块级轻量 | 单一有边界模块可逆，且不改变整个 operating model | 模块 I/T/O、owner、验证、回滚路径 |
| 混合方式 | discovery 仍不确定，但最终交付可能影响生产、用户、信任、收入、合规、runtime behavior 或 release safety | 轻量 discovery，随后对受影响交付层级使用完整控制 |

默认应是局部轻量，而不是整体随意。先小启动，再扩展真正承载风险的层级、阶段或模块。只有耦合变成系统性时，才扩展整个项目。

## 内嵌 Codex 治理边界

当一人公司项目使用 Codex CLI 持久化团队时，Codex 是内嵌的执行与治理能力。它负责 AI Agent 执行、代码交付、持久化执行、验证门、发布边界、worktree 卫生和 repo-local durable state。一人公司运营系统负责客户、收入、财务、法务承诺、支持、市场工作和业务学习。

`decision-log.md`、`risk-register.md`、`metrics.md`、`learning-log.md`、`agent-role-map.md`、`agent-permissions.md`、`human-review-checklist.md` 和 `monthly-review.md` 等共享台账只有在每条记录都标明 `scope`、`truth_owner`、`evidence_source`、`decision_right` 和关联证据时才可共用。业务加 Codex 的混合事项必须同时通过业务门和 Codex 执行门。

详细边界由 `docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.zh-CN.md` 治理。

## 与 Codex CLI 持久化团队白皮书的关系

Codex CLI 持久化团队白皮书描述的是帮助个人维护者协调 native Codex、专家短突发、durable lanes、LangGraph、OpenSpec、worktree、发布安全和 repo-local durable state 的平台。

本文描述的是可能消费这些平台能力的下游业务 operating system。两份文件应互相链接，但保持分开：

- 平台白皮书：拥有开发者编排叙事和 runtime 边界。
- 一人公司白皮书：拥有下游 business-operating 叙事和公司系统边界。
- 清单地图：拥有精确数量。
- 生命周期与 PMI 地图：拥有过程语法和裁剪权威。

除非其中一份文件变成没有独立读者、没有单独更新触发器、没有独特下游引用的薄重复文件，否则不要合并。

## 非目标

- 不要求在第一个已验证 offer 前创建全部 60 个文档。
- 不允许 AI Agent 作出最终定价、法务、发布、客户或财务承诺。
- 不把下游客户证据、收入事实、法务事实、支持事实或 durable state 移入平台仓库。
- 不把平台仓库当作未来业务项目的经营真相。
