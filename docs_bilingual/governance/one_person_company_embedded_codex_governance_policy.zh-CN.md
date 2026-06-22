---
doc_id: one_person_company_embedded_codex_governance_policy
doc_class: governance
status: active
canonical_path: docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.md
zh_cn_path: docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.zh-CN.md
translation_of: docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.md
---
# 一人公司内嵌 Codex 治理政策

## 目的

本政策定义 Codex CLI 个人开发者生产级持久化团队如何嵌入个人级生产级一人公司运营系统。Codex 团队是内嵌的平台治理能力，而不是与公司业务真相竞争的平级权威。

## 相关文档

- `docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.zh-CN.md` - 消费内嵌 Codex 治理边界的下游业务运营白皮书。
- `docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.zh-CN.md` - 一人公司业务北极星；混合循环必须双门通过后才可计数。
- `docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.zh-CN.md` - 记录 canonical 命名和内嵌治理收尾的实施方案。
- `docs_bilingual/docs_registry.yaml` - 本政策和已生成运营包正文文档的 registry 权威。
- `docs_bilingual/operations_packages/codex_cli_durable_team/` 与 `docs_bilingual/operations_packages/one_person_company/` - 分离的运营包目录；可以共享 canonical 文件名，但必须保留真相归属。

## 治理关系

```text
个人级生产级一人公司运营
|- 业务经营治理：客户、收入、定价、合同、支持、交付、现金流
|- 内嵌 Codex 治理：Agent、OpenSpec、worktree、durable state、验证门、发布门
`- 共享治理台账：风险、决策、指标、证据、复盘、权限、人审
```

核心规则：

- 一人公司拥有业务真相：客户证据、收入、合同、支持、法务姿态和现金流不由 Codex 平台文档决定。
- Codex 持久化团队拥有执行真相：专家路由、Agent 权限、工具调用、代码变更、worktree、本地 `main`、repo-local durable state、验证门和发布边界由 Codex 执行政策治理。
- 混合事项必须双门审批：任何同时影响客户、收入、合规或承诺，以及代码、Agent、runtime 或发布状态的变更，都必须同时通过业务门和 Codex 执行门。
- AI Agent 不拥有最终承诺权：定价、合同、发布、客户承诺、财务承诺、退款和法务承诺必须由人确认。

## 共享台账契约

以下台账可以作为项目级共享台账，但每条记录必须带有下列 scope 字段：

```yaml
scope: business | codex | mixed
truth_owner: founder | codex-operator | human-review
evidence_source: customer | revenue | repo | runtime | agent | legal
decision_right: human | delegated-draft-only
linked_docs: []
```

建议共享的台账：

| 台账 | 共用方式 |
| --- | --- |
| `decision-log.md` | 一份决策日志，按 `business`、`codex` 或 `mixed` 标记。 |
| `risk-register.md` | 一份风险登记册，区分业务风险、平台风险和混合风险。 |
| `learning-log.md` | 一份学习日志，区分客户学习、运营学习和平台学习。 |
| `experiment-log.md` | 一份实验日志，区分市场实验、产品实验和 Agent/自动化实验。 |
| `data-dictionary.md` | 一份数据字典，分出业务数据、遥测数据和 Agent 状态数据。 |
| `tracking-plan.md` | 一份追踪计划，区分业务事件和平台执行事件。 |
| `backup-restore.md` | 一份恢复手册，分出业务数据、repository 和 durable-state 小节。 |
| `agent-role-map.md` | 一份 Agent 角色图，区分业务 Agent 和 Codex 执行 Agent。 |
| `agent-permissions.md` | 一份权限矩阵，按工具、数据和审批权拆分。 |
| `human-review-checklist.md` | 一份人工评审清单，覆盖业务承诺和 Codex 执行门。 |
| `monthly-review.md` | 一份月度复盘，同时复盘业务循环质量和平台执行质量。 |

## 同名文件，真相分区

部分文档可以在两个运营包目录中使用相同 canonical 文件名。文件名表达共享语义，内容仍然保留各自 package 的事实边界。

| canonical 文件名 | 一人公司真相 | Codex 持久化团队真相 |
| --- | --- | --- |
| `vision.md` | 公司愿景。 | 平台能力愿景。 |
| `strategy.md` | 市场与收入战略。 | 平台演进战略。 |
| `business-model.md` | 客户与收入模型。 | 生产力与成本模型。 |
| `pricing.md` | 客户定价。 | 平台成本或套餐假设。 |
| `unit-economics.md` | 客户经济性。 | 自动化与执行经济性。 |
| `user-segments.md` | 客户与买方。 | 开发者与项目类型。 |
| `market-map.md` | 业务市场。 | 工具与平台替代方案。 |
| `north-star.md` | 业务循环吞吐量。 | 编排与交付可靠性。 |
| `metrics.md` | 业务指标。 | 执行与治理指标。 |
| `prd.md` | 客户产品 PRD。 | 平台能力 PRD。 |
| `tech-stack.md` | 业务 runtime 依赖。 | Codex tooling 依赖。 |
| `privacy-policy.md` | 客户隐私承诺。 | 工具、日志和状态数据处理。 |

## 必须区分但统一语义的文件

下列文件不能合并成同一份事实文件，但必须使用兼容术语并链接证据：

| Codex 文档 | 一人公司文档 | 统一语义 |
| --- | --- | --- |
| `thesis.md` | `thesis.md` | 为什么系统存在、服务谁、拒绝什么。 |
| `agent-governance.md` | `agent-governance.md` | Agent 能做什么、不能做什么、何时需要人审。 |
| `agent-evaluation.md` | `agent-governance.md` / `human-review-checklist.md` | Agent 质量、失败模式和验收门。 |
| `agent-failure-modes.md` | `risk-register.md` | Agent 风险分类与响应。 |
| `architecture.md` | `automation-map.md` | 系统结构与自动化结构。 |
| `adr.md` | `decision-log.md` | 架构决策与业务决策使用共同记录语法。 |
| `module-boundaries.md` | `tool-stack.md` / `api-dependency-map.md` | 模块边界、工具边界和外部依赖边界。 |
| `delivery-plan.md` | `roadmap.md` / `quarterly-plan.md` | 交付计划与业务路线图。 |
| `observability.md` | `funnel-dashboard.md` / `metrics.md` | 运行时可观测性与经营仪表盘。 |
| `security-policy.md` | `legal-checklist.md` / `compliance-checklist.md` | 安全控制与合规控制。 |
| `access-control.md` | `agent-permissions.md` | 访问权、操作权和审批权。 |
| `incident-response.md` | `support-playbook.md` / `feedback-triage.md` | 事故响应与客户反馈响应。 |
| `support-playbook.md` | `customer-success-playbook.md` / `support-playbook.md` | 平台支持与客户支持。 |
| `cli-ux.md` | `onboarding.md` / `service-blueprint.md` | 操作体验与客户/服务体验。 |
| `changelog.md` | `roadmap.md` / `monthly-review.md` | 变更记录与经营复盘。 |
| `postmortem.md` | `learning-log.md` | 事故复盘与经营学习。 |
| `template-library.md` | `content-calendar.md` / `landing-page.md` | 平台模板资产与市场内容资产。 |

## 绝不能混用的真相

只能归一人公司治理：

- `offer.md` - 记录面向客户的承诺和价值包装。
- `finance-model.md` - 拥有收入、成本、runway 和可持续假设。
- `cashflow.md` - 跟踪现金时点、义务和生存约束。
- `contract-template.md` - 治理客户或合作方合同语言。
- `terms-of-service.md` - 治理面向客户的服务条款和承诺。
- `sales-playbook.md` - 治理销售动作、资格判断和经人确认的承诺。
- `customer-success-playbook.md` - 治理客户成功结果和关系节奏。
- `refund-policy.md` - 治理退款规则、例外处理和客户补救。
- `legal-checklist.md` - 治理法务评审触发器和必需的人类确认。
- `compliance-checklist.md` - 治理监管、隐私和合规评审触发器。

只能归 Codex 治理：

- `architecture.md` - 记录平台系统结构和技术边界。
- `adr.md` - 记录架构决策和执行取舍。
- `module-boundaries.md` - 记录代码、工具和集成边界。
- `observability.md` - 记录 runtime 遥测和交付可靠性控制。
- Codex 包内的 `agent-governance.md`
- `agent-evaluation.md` - 治理 Agent 质量检查和验收证据。
- `agent-failure-modes.md` - 治理 Agent 失败分类和缓解措施。
- `access-control.md` - 治理平台访问权、操作权和审批权。
- `incident-response.md` - 治理平台事故和恢复动作。
- `delivery-plan.md` - 治理代码交付、验证门和发布边界。

## 推荐表述

下游文档应使用以下表述：

> 在个人级生产级一人公司运营中，Codex CLI 个人开发者生产级持久化团队是嵌入式执行与治理能力。它负责 AI Agent、代码交付、持久化执行、验证、发布边界和 repo-local durable state；一人公司运营系统负责客户、收入、财务、法务承诺、支持、市场工作和业务学习。两者共享风险、决策、证据、复盘和人审语义，但不得混用业务真相与平台真相。
