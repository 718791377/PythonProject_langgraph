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
