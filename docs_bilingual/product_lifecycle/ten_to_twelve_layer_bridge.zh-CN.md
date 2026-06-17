---
doc_id: ten_to_twelve_layer_bridge
lang: zh-CN
canonical: docs_bilingual/product_lifecycle/ten_to_twelve_layer_bridge.md
translation_of: docs_bilingual/product_lifecycle/ten_to_twelve_layer_bridge.md
doc_class: product_lifecycle
status: draft
---

# 10 到 12 层桥接

本文解释为什么研究稿与白皮书应继续分离、它们的分层模型如何连通，以及如何双向阅读而不混淆职责。

## Canonical Roles

- 研究稿拥有 canonical 的 10 层 runtime/governance capability model。
- 白皮书拥有 Codex CLI 平台 canonical 的 12 层 product/business lifecycle narrative。
- 本 bridge 只拥有两者之间的 mapping grammar。
- 本 bridge 不得重写研究模型，也不得替代 lifecycle stack。

## 文件关系

- 研究稿使用 10 层运行时/治理拆分，研究一个 solo-maintainable persistent team 在执行时必须具备什么能力。
- 白皮书使用仓库 12 层产品/商业生命周期，说明为什么 Codex CLI durable-team 平台应该存在，以及如何变得可治理。
- 现在不应物理合并二者，因为它们的受众、审查路径和下游引用不同。

## 阅读模式

### Read 10 -> 12

当 runtime finding 需要 lifecycle owners、documents、release gates 或 platform-facing explanation 时，使用这个方向。

此模式下的问题：

- 哪个 lifecycle layer 接收这个 runtime capability？
- 哪份文档应拥有由此产生的 requirement？
- 哪个 owner、metric、runbook 或 release gate 需要更新？

### Read 12 -> 10

当 white-paper 或 lifecycle claim 需要证明 runtime 真的能支撑它时，使用这个方向。

此模式下的问题：

- 哪个 runtime capability 让这个 lifecycle claim 成立？
- 在这个 lifecycle claim 可信之前，必须有哪些 research-layer evidence？
- 哪些 runtime gaps 会阻塞这个 lifecycle promise？

## 10 -> 12 Bridge Table

下表是“桥接时的聚合视图”，不是研究稿 10 层运行时模型的 canonical 替代表。它把相邻运行时关注点聚合起来，目的是让每个关注点可以落到合适的 12 层生命周期文档、owner 和 gate。

| 10 层研究模型 | 主要 12 层落点 | 次要 12 层落点 | Bridge rule |
| --- | --- | --- | --- |
| Interaction and execution | Product、Execution | Operations | 把 runtime interaction capability 转成 product promises、execution workflow、operating runbooks 与 safe user expectations |
| Team orchestration | Organization、Execution | Operations | 把 worker/leader coordination 转成 responsibility domains、agent governance、escalation paths 与 execution gates |
| Agent state persistence | Technical、Operations | Retrospective | 把 state fields 转成 architecture contracts、recovery evidence、migration rules 与 post-incident learning |
| Task-flow persistence | Technical、Execution | Operations | 把 workflow state 转成 plan checkpoints、resumption rules 与 governed execution handoffs |
| Memory and context | Cognitive Narrative、Technical | Operations、Retrospective | 把 memory capability 转成 cold-start understanding、context-store design、retention policy 与 learning feedback |
| Retrieval and knowledge | Growth、Technical | Metrics、Retrospective | 把 retrieval 转成 knowledge reuse、source maps、quality evidence 与 compounding learning loops |
| Quality and evaluation | Metrics、Execution | Retrospective | 把 evaluation 转成 acceptance gates、regression checks、release criteria 与 lessons learned |
| Security and governance | Organization、Technical | Operations | 把 security constraints 转成 trust boundaries、ownership rules、operating controls 与 approval discipline |
| Observability and audit | Metrics、Operations | Retrospective | 把 observability 转成 guardrails、trace evidence、closure evidence 与 learning assets |
| Control center and operator surface | Cognitive Narrative、Product、Organization | Operations | 把 operator surfaces 转成 authority boundaries、recoverable workflows、incident handling 与 command discipline |

## 12 层接收视图

下表是反向视图：先从生命周期层出发，再判断通常由哪些 10 层 runtime concerns 输入。

| 12 层生命周期层 | 通常输入的 10 层关注点 | 为什么该层接收它们 |
| --- | --- | --- |
| 0. 认知叙事 | memory/context；control center；auditability | operator 需要稳定叙事、可恢复 mental model 与可见 authority surfaces |
| 1. 商业 | interaction/execution；quality/evaluation；recovery cost | 商业价值依赖平台是否能以可维护成本可靠地产出有用工作 |
| 2. 市场 | interaction/execution；quality/evaluation；observability/audit | 市场定位依赖可见能力、可靠性和信任证据 |
| 3. 战略 | security/governance；team orchestration；persistence boundary | 战略拥有 local-first posture、backend-family separation 与 solo-maintainer control |
| 4. 指标 | retrieval/knowledge；quality/evaluation；observability/audit | 指标让 runtime quality、cost 与 evidence 可检查 |
| 5. 产品 | interaction/execution；control center；team orchestration | 产品形态是执行能力与控制设计的用户可见表达 |
| 6. 技术 | agent state persistence；task-flow persistence；retrieval/storage；security | 架构接收 runtime mechanisms 与 trust constraints |
| 7. 组织 | team orchestration；security/governance；control center | ownership、role discipline 与 authority boundaries 属于此层 |
| 8. 执行 | interaction/execution；task-flow persistence；quality assurance | 交付流依赖 coordination、checkpointing 与 acceptance behavior |
| 9. 增长 | retrieval/knowledge；memory/context；evaluation | 增长来自复用、知识复利与可度量改进 |
| 10. 运营 | persistence；task-flow persistence；memory/context；observability；security | 运营拥有 recovery、incidents、runbooks 与 day-two controls |
| 11. 复盘 | memory/context；retrieval/knowledge；evaluation；audit | 复盘把 runtime evidence 转成修正和可复用学习 |

## 12 层新增语境

12 层生命周期新增了 10 层运行时研究不直接拥有的业务与治理主干：认知叙事、商业、市场、战略、指标、产品、组织、执行、增长、运营和复盘学习。其中认知叙事、商业、市场和增长是最明显的新增主干。它们不是 runtime capability analysis 的替代品，而是把 runtime capability 变成平台时需要的更大框架。

## 桥接执行语法

当 10 层运行时发现需要转成 12 层生命周期工作，或 12 层主张需要 10 层 runtime proof 时，使用以下过程组式语法。

### 输入

- 来自研究稿的层级、能力缺口、来源证据、成熟度判断或运行时风险。
- 被检查的 lifecycle-layer claim、product statement、operating rule 或 retrospective conclusion。
- 目标生命周期模式：Codex CLI 持久化团队平台，或下游一人公司经营系统。
- fresh-source evidence 边界、清单数量权威、受影响层级 owner，以及当前 OpenSpec 或交付状态。
- 安全、durable state、operator authority、release safety、预算和下游项目 ownership 约束。

### 工具与技术

- 桥接时聚合：把相邻 runtime 关注点聚合，但不重命名研究稿 canonical 模型。
- 接收视图查找：选择哪个 12 层生命周期层接收该 runtime 发现。
- 反向证明查找：选择哪些 10 层关注点必须被引用，才能证明一个 lifecycle claim。
- 权威拆分复核：runtime capability 权威保留在研究稿，叙事权威保留在白皮书，数量权威保留在 inventory maps，PMI 权威保留在 PMI reference map，执行语法保留在 lifecycle 文档。
- 裁剪复核：判断结果需要完整架构、整个项目轻量、阶段局部轻量、模块级轻量，还是混合治理。
- I/T/O 展开：若桥接结果驱动执行，则在接收方 lifecycle 文档或 OpenSpec change 中展开为输入、工具与技术、输出。

### 输出

- runtime 发现对应的命名 12 层落地区域。
- lifecycle claim 对应的命名 10 层证明路径。
- 不合并职责前提下更新的 lifecycle、白皮书、研究稿、北极星或 OpenSpec 引用。
- 受影响范围的裁剪决策与执行语法。
- 可追溯证据，说明当前使用哪个模型以及哪个文档拥有该结果。

## 治理规则

评估 runtime capability completeness、state、orchestration、memory、auditability 与 operator control 时使用 10 层模型。判断平台或下游一人公司是否具备足够 narrative、business、market、strategy、metrics、product、technical、organization、execution、growth、operations 与 retrospective evidence 时使用 12 层模型。一个文档如果同时引用二者，必须说明当前使用的是哪个模型、结果落到哪个生命周期层，以及由哪个研究层证据支撑。

数量权威保留在 `codex_platform_inventory_map.zh-CN.md` 与 `one_person_company_inventory_map.zh-CN.md`。runtime capability 权威保留在 `solo_maintainable_production_persistent_team_research.zh-CN.md`。叙事权威保留在 `codex_cli_personal_production_durable_team_whitepaper.zh-CN.md`。本文只拥有这些权威之间的映射关系。
