# codex-product-lifecycle-document-governance 规格

## Purpose

定义本仓库的产品与商业文档生命周期图，并保持 Codex 平台建设文档和下游项目消费平台能力文档相互分离。

## Requirements

### Requirement: Product Lifecycle Reference Defines The 0-8 Document Stack

仓库必须维护一份双语产品生命周期参考，定义认知叙事、商业、市场、战略、产品、技术、执行、增长和复盘层。

#### Scenario: A maintainer asks how a white paper differs from a North Star plan

- **GIVEN** 维护者阅读产品生命周期参考
- **WHEN** 维护者比较文档类型
- **THEN** 该参考说明白皮书用于改变认知，并解释为什么该方向存在
- **AND** 该参考说明北极星 Plan 用于把战略转化为可衡量方向、指标、杠杆和分阶段执行

### Requirement: Platform Build And Project Consumption Stay Separate

仓库必须把 Codex CLI durable-team 平台建设生命周期，与后续项目消费该平台的生命周期分开记录。

#### Scenario: A later project uses the platform templates

- **GIVEN** 后续项目接收 templates、user-level runtime policies 和 subagent profiles
- **WHEN** 该项目开始自己的工作
- **THEN** 该项目拥有自己的 `AGENTS.md`；这是项目级 Codex 指令文件
- **AND** 该项目拥有自己的 `openspec/`；这是项目本地 OpenSpec 治理树
- **AND** 该项目拥有自己的 `.omx/state/`；这是项目本地 durable truth 目录

### Requirement: Platform Documents May Define Shared Governance But Not Business Runtime Truth

Codex 平台仓库可以定义可复用 governance、templates、checkers、role policies、release gates 和 shared tooling，但不得成为下游业务项目的 repo-local durable truth。

#### Scenario: A business project learns a reusable governance lesson

- **GIVEN** 经验教训来自下游业务项目
- **WHEN** 该经验足够通用，可以改进平台
- **THEN** 该项目必须先把它记录为 upstream feedback
- **AND** 平台只能通过平台 OpenSpec change 采纳该经验

### Requirement: PMI References Are A Governance Overlay

仓库必须把 PMI 项目管理参考资料作为 delivery、tailoring、quality、risk、change control 和 closing 的治理叠加层，而不是用它替代产品与商业生命周期。

#### Scenario: A maintainer adds PMI guidance to lifecycle docs

- **GIVEN** 维护者把 `PMP/` 作为本地私有参考目录；该目录保存本地参考资料并继续被 Git 忽略
- **WHEN** 维护者更新仓库生命周期文档
- **THEN** 更新内容只能总结本仓库特定映射
- **AND** 更新内容不得复制 PMI 书籍正文
- **AND** 本地 `PMP/` 参考目录继续被 Git 忽略

### Requirement: Process Groups Map To OpenSpec Delivery Gates

仓库必须把 PMI process group model 映射到 OpenSpec 和 GitLab-first delivery gates。OpenSpec 是仓库治理工作流；GitLab-first delivery gates 是以 GitLab MR 和 pipeline 为权威评审门的交付流程。

#### Scenario: A platform change moves from idea to archive

- **GIVEN** 平台 change 通过 OpenSpec 和 GitLab 管理
- **WHEN** 该 change 被规划和交付
- **THEN** initiating 映射到 proposal 和类似 project charter 的范围定义
- **AND** planning 映射到 design、tasks、risks、validation、release 和 rollback planning
- **AND** executing 映射到 implementation work
- **AND** monitoring and controlling 映射到 checkers、pipeline、diff review 和 change control
- **AND** closing 映射到 archive、stable spec sync 和 lessons learned

### Requirement: Agile Guidance Supports Exploratory And Hybrid Work

仓库必须把 agile guidance 用于不确定、探索型、MVP 和反馈驱动工作，同时为高风险或范围清晰的交付保留 predictive process gates。

#### Scenario: A task is not yet clear enough for implementation

- **GIVEN** 请求的工作仍存在未解决的市场、产品或技术不确定性
- **WHEN** leader 选择执行方式
- **THEN** 工作先从小型 exploration、spike 或 MVP slice 开始
- **AND** 在计划冻结且存在独立执行切片之前，不启动 durable team

### Requirement: Platform White Paper And MRD Are First-Class Lifecycle Documents

仓库 SHALL 维护 Codex CLI personal production durable-team platform 的第一类双语 white paper 和 MRD 文档，然后才能把下游 implementation plans 视为完整 lifecycle coverage。

#### Scenario: A maintainer follows the lifecycle stack

- **GIVEN** 维护者阅读 platform lifecycle documentation（平台生命周期文档）
- **WHEN** 维护者需要 cognitive narrative（认知叙事）和 market requirements（市场需求）
- **THEN** 维护者可以在 `docs_bilingual/whitepapers/` 找到 canonical white paper；`docs_bilingual/whitepapers/` 是白皮书目录，用来保存认知叙事文档
- **AND** 维护者可以在 `docs_bilingual/market_requirements/` 找到 MRD；`docs_bilingual/market_requirements/` 是市场需求目录，用来保存 market-requirements documents
- **AND** concrete workload-to-profile mappings（具体工作负载到 profile 的映射）位于 MRD appendix，而不是单独的 implementation-plan reference
