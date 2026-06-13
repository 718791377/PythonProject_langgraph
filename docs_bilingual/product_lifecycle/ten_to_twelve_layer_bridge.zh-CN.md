# 10 层到 12 层桥接

本文解释为什么研究稿与白皮书仍保持分离，以及两种分层模型如何打通。

## 文件关系

- 研究稿使用 10 层运行时/治理拆分，研究一个 solo-maintainable persistent team 在执行时必须具备什么能力。
- 白皮书使用仓库 12 层产品/商业生命周期，说明为什么 Codex CLI durable-team 平台应该存在，以及如何变得可治理。
- 现在不应物理合并二者，因为它们的受众、审查路径和下游引用不同。

## 桥接表

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

## 治理规则

评估 runtime capability completeness、state、orchestration、memory、auditability 与 operator control 时使用 10 层模型。判断平台或下游一人公司是否具备足够 business、market、product、delivery、operations 与 learning evidence 时使用 12 层模型。一个文档如果同时引用二者，必须说明当前使用的是哪个模型，以及结果落到哪个生命周期层。
