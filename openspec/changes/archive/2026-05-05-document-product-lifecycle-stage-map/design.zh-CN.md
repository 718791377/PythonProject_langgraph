# Design

## Placement

本 change 新增 `docs_bilingual/product_lifecycle/` 目录；这是产品与平台生命周期参考区，用来放比单个 implementation plan 更上层的规划概念。

该目录包含三组双语文档：

- `product_business_document_lifecycle.md` 是 0-8 产品与商业文档阶段的 ASCII 主参考。
- `product_business_document_lifecycle.zh-CN.md` 是同一 0-8 阶段的 UTF-8 中文对照版。
- `codex_durable_team_platform_build_lifecycle.md` 是建设 Codex CLI durable-team 平台本身的 ASCII 主参考。
- `codex_durable_team_platform_build_lifecycle.zh-CN.md` 是平台建设阶段的 UTF-8 中文对照版。
- `codex_project_consumption_lifecycle.md` 是后续项目消费平台能力的 ASCII 主参考。
- `codex_project_consumption_lifecycle.zh-CN.md` 是项目消费阶段的 UTF-8 中文对照版。

## Boundary Model

平台建设生命周期和项目消费生命周期必须保持分离。

平台建设文档属于 `D:\PythonProject_langgraph`；这是 Codex 编排源码仓库。它可以定义可复用规则、模板、checker、OpenSpec 治理、subagent profiles、durable backend policies、release gates 和共享工具。

项目消费文档属于每个后续项目自己的仓库。后续项目可以使用共享用户级 runtime 和模板，但必须拥有自己的 `AGENTS.md`、自己的 `docs_bilingual/project_startup_summary.md`、自己的 `openspec/` 树和自己的 `.omx/state/` durable truth。

## Stage Model

通用 0-8 模型保持产品中立：

0. 认知叙事层。
1. 商业决策层。
2. 市场需求层。
3. 战略与北极星层。
4. 产品定义层。
5. 技术设计层。
6. 执行与交付层。
7. 增长与采用层。
8. 复盘与学习层。

Codex 平台建设参考把每个阶段映射到平台文档。项目消费参考把同一阶段逻辑映射到后续项目，并明确说明小项目可以省略哪些文档。

## Validation

本 change 只修改文档。验证使用 OpenSpec 和仓库文档 checker，不使用 runtime tests。
