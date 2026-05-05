# 记录产品生命周期阶段图

## Why

生产级持久化团队方案现在涉及多种规划概念：白皮书、BRD、MRD、北极星 Plan、PRD、技术设计、implementation plan、增长计划和复盘记录。这些文件用途不同，仓库需要一份小而稳定的参考说明，并严格区分两条流程：

1. 建设 Codex CLI 个人开发者生产级持久化团队平台。
2. 后续具体项目使用该平台。

如果不区分，后续维护者可能会把业务项目文档写进平台方案，或者误把平台仓库当成消费项目的 durable truth。

## What Changes

- 新增双语产品与商业文档生命周期参考。
- 新增双语 Codex CLI durable-team 平台建设生命周期参考。
- 新增双语后续项目消费平台能力的生命周期参考。
- 新增 OpenSpec 需求，要求平台建设文档和项目使用文档保持分离。

## Non-Goals

- 不实现 runtime behavior；这里指实际运行时行为。
- 不启动 `native_omx`；这是面向 worker-centric execution 的 durable-team backend lane。
- 不启动 `langgraph`；这是图式 checkpoint 和 approval-gate backend lane。
- 不写入 `.omx/state/`；这是仓库本地 durable state 目录。
- 不修改用户级 Codex 配置。
