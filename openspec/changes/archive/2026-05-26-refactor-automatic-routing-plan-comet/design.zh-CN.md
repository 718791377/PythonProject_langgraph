## Context

这是 documentation-only Comet tweak。目标计划已是 automatic collaboration routing 的 active baseline，但当前完成证据、Phase 4 planned work、evidence contracts、task list、risks 与 acceptance criteria 的阅读路径不够集中。

当前 Windows shell 不提供 `bash`，因此 Comet shell helpers 无法直接执行。该 tweak 使用显式 OpenSpec artifacts、`.comet.yaml` blocker note 与仓库验证证据作为 fallback。

## Goals / Non-Goals

目标：增加阅读地图和 Comet traceability，澄清 Phase 0-3 完成与 Phase 4 planned follow-up 的边界，并避免复制终端乱码。

非目标：不新增 runtime implementation，不新增 checker，不改 stable governance policy，不合入 local main 或发布远端。

## Decisions

采用 Comet `tweak`，因为它是单文档结构整理，不引入新 capability、架构、接口或依赖。Comet helper 不可用要记录为 blocker，而不是伪造 transition 成功。
