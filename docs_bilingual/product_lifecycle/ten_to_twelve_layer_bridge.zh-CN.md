# 10 层到 12 层桥接

本文解释为什么研究稿与白皮书仍保持分离，以及两种分层模型如何打通。

## 文件关系

- 研究稿使用 10 层运行时/治理拆分，研究一个 solo-maintainable persistent team 在执行时必须具备什么能力。
- 白皮书使用仓库 12 层产品/商业生命周期，说明为什么 Codex CLI durable-team 平台应该存在，以及如何变得可治理。
- 现在不应物理合并二者，因为它们的受众、审查路径和下游引用不同。

## 桥接表

下表是“桥接时的聚合视图”，不是研究稿 10 层运行时模型的 canonical 替代表。它把相邻运行时关注点聚合起来，目的是让每个关注点可以落到合适的 12 层生命周期文档、owner 和 gate。

| 10 层研究模型 | 12 层生命周期落点 | 桥接规则 |
| --- | --- | --- |
| 交互与执行 | 产品、执行、运营 | 把运行时交互能力转成产品承诺、执行流程和运行手册 |
| 团队编排 | 组织、执行 | 把 worker/leader 协作转成责任域、Agent 治理和执行门禁 |
| Agent 状态持久化 | 技术、运营 | 把状态字段转成架构契约与运营恢复证据 |
| 任务流持久化 | 技术、执行、运营 | 把 workflow state 转成计划、checkpoint、恢复规则和 runbook |
| 记忆与上下文 | 认知叙事、技术、运营 | 把记忆能力转成 cold-start narrative、context-store 设计和保留运营 |
| 检索与知识 | 指标、技术、增长 | 把检索转成证据指标、source map 和可复用学习闭环 |
| 质量/评测 | 指标、执行、复盘 | 把评测转成验收门、回归检查和经验教训 |
| 安全/治理 | 技术、组织、运营 | 把安全约束转成信任边界、审批和运行控制 |
| 可观测/审计 | 指标、执行、运营、复盘 | 把可观测性转成指标护栏、trace evidence 和 closure records |
| 控制中心/操作员表面 | 认知叙事、组织、运营 | 把控制表面转成可恢复的 operator workflow 与权限边界 |

## 12 层新增语境

12 层生命周期新增了 10 层运行时研究不直接拥有的四个面向业务的主干：认知叙事、商业、市场与增长。它们解释目的、价值、采用和学习。

## 桥接执行语法

当 10 层运行时发现需要转成 12 层生命周期工作时，使用以下过程组式语法。

### 输入

- 来自研究稿的层级、能力缺口、来源证据、成熟度判断或运行时风险。
- 目标生命周期模式：Codex CLI 持久化团队平台，或下游一人公司经营系统。
- fresh-source evidence 边界、清单数量权威、受影响层级 owner，以及当前 OpenSpec 或交付状态。
- 安全、durable state、operator authority、release safety、预算和下游项目 ownership 约束。

### 工具与技术

- 桥接时聚合：把相邻 runtime 关注点聚合，但不重命名研究稿 canonical 模型。
- 落地区域分配：选择哪个 12 层生命周期层接收该 runtime 发现。
- 权威拆分复核：runtime capability 权威保留在研究稿，叙事权威保留在白皮书，数量权威保留在 inventory maps，PMI 权威保留在 PMI reference map，执行语法保留在 lifecycle 文档。
- 裁剪复核：判断结果需要完整架构、整个项目轻量、阶段局部轻量、模块级轻量，还是混合治理。
- I/T/O 展开：若桥接结果驱动执行，则在接收方 lifecycle 文档或 OpenSpec change 中展开为输入、工具与技术、输出。

### 输出

- runtime 发现对应的命名 12 层落地区域。
- 不合并职责前提下更新的 lifecycle、白皮书、研究稿、北极星或 OpenSpec 引用。
- 受影响范围的裁剪决策与执行语法。
- 可追溯证据，说明当前使用哪个模型以及哪个文档拥有该结果。

## 治理规则

评估 runtime capability completeness、state、orchestration、memory、auditability 与 operator control 时使用 10 层模型。判断平台或下游一人公司是否具备足够 business、market、product、delivery、operations 与 learning evidence 时使用 12 层模型。一个文档如果同时引用二者，必须说明当前使用的是哪个模型，以及结果落到哪个生命周期层。

数量权威保留在 `codex_platform_inventory_map.zh-CN.md` 与 `one_person_company_inventory_map.zh-CN.md`。runtime capability 权威保留在 `solo_maintainable_production_persistent_team_research.zh-CN.md`。叙事权威保留在 `codex_cli_personal_production_durable_team_whitepaper.zh-CN.md`。本文只拥有这些权威之间的映射关系。
