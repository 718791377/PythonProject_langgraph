---
doc_id: personal_production_one_person_company_operations_north_star
lang: zh-CN
canonical: docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md
translation_of: docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md
doc_class: north_star_plan
status: draft
---

# 个人级生产级一人公司运营北极星

## 目的

本北极星定义个人经营者如何判断一人公司运营系统是否正在产生经过验证的业务进展，同时避免对低风险工作过度文档化。它与 `docs_bilingual/north_star_plan.zh-CN.md` 中的 Codex CLI 持久化团队平台北极星保持分离。

## 证据边界

本文基于 `one-person-company-pmi-refresh-stageb-20260619` 对 `Business Management/` 与 `PMP/` 的 fresh extraction，以及 `one-person-company-pmi-refresh-stageb-product-lifecycle-20260619` 对当前生命周期 Markdown 文件的全文读取。本文只记录聚合证据和仓库特定综合结论。

## 主指标

**已验证运营循环吞吐量** 指在一个评审周期内满足以下条件的运营循环数量：

1. 从客户证据、商业证据、支持证据、财务证据或风险证据启动；
2. 通过受影响层级、阶段或模块所需的裁剪门；
3. 产出已交付、已销售、已支持、已验证或已退役的业务输出；
4. 对任何影响客户、收入、法务、财务、发布或支持承诺的受治理 Agent 输出记录人工评审；
5. 把学习回流到下一次月度复盘、指标契约、风险登记册或运营手册。

该指标计数的是已验证循环，而不是原始任务、字数、commit 或 Agent 消息数。

## 输入指标

| 输入指标 | 衡量内容 | 示例证据 |
| --- | --- | --- |
| 客户证据循环 | 真实客户或用户证据改变 offer、细分、产品、支持规则或定位决策的频率 | 访谈记录、反馈分流、支持工单、采用信号 |
| 收入与现金循环 | 在承诺增长前是否复核商业模式、定价、现金流和 runway | `pricing.md`、`finance-model.md`、`cashflow.md`、单位经济 note |
| 交付稳定性循环 | 已交付工作是否可验证、可支持、可回滚 | 验证说明、发布说明、回滚说明、问题日志 |
| 支持负载循环 | 支持需求是否转化为运营改进，而不是保持隐藏 | 支持政策、FAQ 更新、客户成功 note |
| 学习节奏循环 | 决策和事故是否变成可复用学习 | `monthly-review.md`、学习日志、决策日志 |
| 受治理 Agent 评审循环 | 影响承诺的 AI Agent 输出是否由人类 owner 评审 | Agent 评审清单、权限说明、人工签字 |

## 护栏

| 护栏 | 破坏信号 | 必需响应 |
| --- | --- | --- |
| 未评审 AI 承诺 | Agent 未经人工评审起草或发送客户、法务、财务、发布、定价或支持承诺 | 停止、复核，并更新 `agent-governance.md` |
| Runway 与现金风险 | 承诺增长时现金、成本或定价假设变旧 | 扩大范围前重新执行财务复核 |
| 支持风险 | 交付产生支持义务，但没有支持政策、FAQ 或升级路径 | 发布或承诺前扩展运营层 |
| 隐私与合规风险 | 工作触达个人数据、敏感数据、合同、受监管声明或安全边界 | 扩展治理层和技术层，不得保持轻量 |
| 过度文档化拖拽 | 文档增长没有客户、收入、风险、支持或学习价值 | 收缩到最小充分文档，并记录裁剪决策 |

## 决策阈值

| 决策 | 触发条件 | 行动 |
| --- | --- | --- |
| 对受影响范围使用完整架构 | 出现外部用户、金钱、敏感数据、合规、信任、支持义务、重复交付、广泛 Agent 自动化或高回滚成本 | 把受影响层级扩展到完整 I/T/O、owner、风险、验证、发布/回滚和复盘证据 |
| 保持整个项目轻量 | 工作私有、可逆、低风险、单 owner，且无外部用户、金钱、敏感数据、支持承诺、共享 runtime 或发布承诺 | 使用 12 个最小启动文档或紧凑等价物，并保留验证与学习 note |
| 使用阶段局部轻量 | discovery、原型、访谈、内容探索或指标探索在较大治理工作中风险较低 | 只在该阶段轻量，并定义扩展触发器 |
| 使用模块级轻量 | 有边界模块可逆，且不改变 operating model、信任边界、客户承诺、durable state、公开 API 或发布安全 | 保留模块 I/T/O、owner、验证、回滚或删除路径和学习 note |
| 使用混合模式 | 不确定性高，但可能交付会影响生产、用户、收入、信任、合规、runtime behavior 或 release safety | 先适应式探索；外部影响前冻结预测式过程组控制 |
| 停止或转向 | 循环反复产生负面证据、无客户拉力、runway 压力、支持过载或未解决信任/合规风险 | 在增加文档或自动化前停止、转向或缩小范围 |

## 过程组式运行节奏

| 过程组 | 输入 | 工具与技术 | 输出 |
| --- | --- | --- | --- |
| 启动 | 客户或运营信号、候选循环、当前裁剪状态、owner 容量 | 价值 framing、风险扫描、停止条件 framing | 循环章程、owner、初始裁剪决策 |
| 规划 | 循环章程、12 层影响、现金/支持约束、Agent 边界 | 裁剪评分卡、验证设计、人工评审设计 | 循环计划、输入指标、护栏、验证路径 |
| 执行 | 已批准循环计划、最小文档、Agent 权限、客户或运营证据 | 发现、交付、销售、支持、测量、受治理 Agent 起草 | 循环输出、证据包、变更后的文档或运营资产 |
| 监控与控制 | 指标、支持负载、现金/runway 信号、风险登记册、Agent 评审证据 | 指标复核、护栏复核、变更控制、回滚/停止复核 | 继续/扩展/停止决策、问题更新、护栏响应 |
| 收尾 | 循环输出、决策、学习、残余风险 | 月度复盘、决策归档、手册更新、下周期优先级排序 | 已归档循环、更新后的政策或指标、下周期输入 |

## 非目标

- 不把本北极星当作任务清单。
- 除非通过人工和运营循环验证，否则不把 Agent 活动量当作业务进展。
- 不用本北极星替代项目自己的客户、财务、法务、支持或发布记录。

## 内嵌 Codex 门

如果被计量的循环同时改变代码、Agent、runtime、worktree、durable state、验证门、发布边界或仓库证据，则该循环属于混合循环。混合循环只有在 `docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.zh-CN.md` 规定的业务门和 Codex 执行门都通过后，才能计入北极星。

## Stage B Embedded Governance Closeout

This Stage B closeout makes the nested relationship explicit: the one-person company owns business truth, and embedded Codex owns governed execution truth. Embedded Codex is not a peer business authority and must not redefine business truth.

- One-person company boundary: the one-person company owns business truth for customers, revenue, pricing, contracts, legal posture, cashflow, support, delivery commitments, and business learning; embedded Codex supplies execution evidence and automation support.
- Tailoring modes: full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, and hybrid are all scoped choices. Tailoring does not delete the twelve-layer mental model; it only changes how much evidence and ceremony is required for the chosen project, phase, module, or release slice.
- Bridge rule: the 10-layer runtime capability view is an implementation projection of the 12-layer lifecycle view. The bridge prevents runtime convenience from overriding lifecycle authority.

### Inputs

- Current business intent, execution evidence, registry entry, tailoring decision, and local-main / remote-publication boundary.
- Business truth inputs when customers, revenue, pricing, contracts, legal posture, cashflow, support, delivery commitments, or business learning are affected.
- Execution truth inputs when agent routing, OpenSpec, worktree isolation, durable state, validation, rollback, or release boundaries are affected.

### Tools And Techniques

- Apply the shared truth-boundary map before selecting full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, or hybrid mode.
- Use process-group I/T/O, RACI ownership, evidence traceability, validation gates, and escalation triggers instead of deleting layers.
- Route mixed changes through both the business gate and the Codex execution gate before local-main integration or remote publication.

### Outputs

- A scoped governance mode, updated evidence trail, linked registry entry, and explicit owner for business truth, execution truth, or mixed truth.
- A closeout decision that either stays lightweight in the declared scope, escalates to fuller architecture, or stops at the publication gate until human approval.
