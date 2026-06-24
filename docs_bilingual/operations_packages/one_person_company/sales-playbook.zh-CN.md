---
doc_id: one_person_company_sales_playbook
doc_class: operations_package
status: active
package: one-person-company
body_kind: growth_and_sales_body
generated_by: tools/generate_operations_package.py
lang: zh-CN
translation_of: docs_bilingual/operations_packages/one_person_company/sales-playbook.md
---

<!-- GENERATED_BY: tools/generate_operations_package.py; DO NOT EDIT BY HAND. -->

# 一人公司 Sales Playbook 正文运营文档

## 目的

定义单人生产级业务运营系统如何在增长与销售文档族中使用 sales-playbook.md 产物，以支持业务决策、证据收集和合适裁剪深度选择。

## 权威边界

- 权威来源：运营白皮书、北极星、Business Management 综合、product lifecycle 清单、PMI 过程组合同和裁剪规则。
- 本文档只运行化本包的单人业务运营规则。
- The one-person company owns business truth for customers, revenue, pricing, contracts, legal posture, cashflow, support, delivery commitments, and business learning.
- Embedded Codex supplies governed execution truth for agents, worktrees, durable state, validation gates, rollback, and release boundaries; it is not a peer business authority and must not redefine business truth.
- 任何外部承诺、收入、合同、隐私或合规影响都必须进入更完整的治理深度。

## 生命周期落点

- 主生命周期层级：L9 增长, L8 执行
- 主过程组：Planning, Executing, Monitoring and Controlling
- 负责人界面：收入与增长办公室
- 文档族：增长与销售；源清单项：`sales-playbook.md`。

## 裁剪规则

默认裁剪模式：混合架构。该选择必须说明为什么不更重也不更轻，并保留升级触发器。

| 模式 | 使用时机 | 轻量范围 |
| --- | --- | --- |
| 完整架构 | 跨阶段、外部客户、收入、合规、安全、发布、回滚、持久状态、共享运行时或多 Agent 工作。 | 端到端治理所有受影响的风险层。 |
| 全项目轻量 | 私有、可逆、低风险探索，并且没有外部承诺、持久状态影响、发布、敏感数据或共享运行时影响。 | 整个项目可以保持轻量，但仍记录负责人、验证、回滚和学习。 |
| 阶段局部轻量 | 更大受治理项目中的某个发现、指标、增长或复盘阶段风险较低。 | 只有被命名的阶段轻量；上下游门禁保持显式。 |
| 模块级轻量 | 单个有边界的文档族、helper、原型或本地模块不改变信任、状态、公共 API、CI、发布或共享运行时行为。 | 只有该模块轻量；周边项目保留完整边界。 |
| 混合架构 | 多数真实工作；低风险阶段可先轻量，但生产、客户、收入、信任、持久状态或发布影响需要更完整控制。 | 关键层完整；低风险阶段或模块在升级触发前保持轻量。 |

### 为什么不更重也不更轻

`sales-playbook.md` 默认采用上述模式，因为 增长与销售 的风险需要被治理，但只有触及外部承诺、敏感信息、共享状态或恢复困难时才需要扩大到更重模式。

### 升级触发器

当范围、信任、合规、收入暴露、恢复难度或跨边界协同超出当前模式记录的假设时，必须升级到更重的裁剪模式。 针对 `sales-playbook.md`，如果 owner 无法确认、证据不可复现、验证路径失效或输出影响外部承诺，也必须升级。

## 输入

- 当前产品、客户、现金流、交付容量、风险、合规和 收入与增长办公室 的 owner 约束。
- `sales-playbook.md` 所属文档族、业务假设、证据来源、依赖和停止或扩展条件。
- 单人 operator 的时间预算、自动化边界和月度复盘输入。

## 工具与技术

- 12 层落点、责任域映射、PMI 过程组 I/T/O、敏捷反馈循环和裁剪评分卡。
- 客户发现、财务检查、渠道实验、服务交付复盘和合规核对。
- 只在外部承诺、收入或风险扩大时升级治理深度。

## 输出

- `Sales Playbook` 的受治理正文、配套 zh-CN companion 和 registry 条目。
- 产品、价格、渠道、支持、财务、合规或知识库中的下一步更新。
- 可在月度复盘中使用的保留、停止、转向、扩展或重新裁剪证据。

## 过程组运行表

| 过程组 | 输入 | 工具与技术 | 输出 |
| --- | --- | --- | --- |
| 启动 | 来源需求、负责人信号、范围边界、首轮风险；文档 `sales-playbook.md` | 章程式界定、干系人扫描、裁剪预检 | 获准继续的运营切片、已命名负责人、初始风险日志 |
| 规划 | 已批准目的、依赖、约束、验收目标；文档 `sales-playbook.md` | I/T/O 规划、RACI 映射、验证设计、回滚设计 | 文档计划、验证路径、回滚边界 |
| 执行 | 已批准切片、模板、证据、本地状态；文档 `sales-playbook.md` | 受控起草、评审、测试、证据捕获 | 已更新运营产物、变更证据、交接记录 |
| 监控 | 活动产物、指标、问题、评审反馈；文档 `sales-playbook.md` | 质量检查、偏差复核、变更控制、门禁重跑 | 问题日志、决策记录、门禁证据 |
| 收尾 | 已验收产物、最终证据、剩余风险；文档 `sales-playbook.md` | 收尾评审、归档或登记同步、复盘 | 最终正文文档、登记条目、经验教训 |

## 收尾与登记

- Registry 中的 `doc_id` 必须保持唯一：`one_person_company_sales_playbook`。
- 英文主文件 `docs_bilingual/operations_packages/one_person_company/sales-playbook.md` 与中文 companion `docs_bilingual/operations_packages/one_person_company/sales-playbook.zh-CN.md` 必须成对更新。
- 收尾时确认 owner、裁剪模式、升级触发器、输出证据和下一周期输入。
