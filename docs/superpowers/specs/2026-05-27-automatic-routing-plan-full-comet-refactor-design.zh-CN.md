# 自动路由方案完整 Comet 重构设计

Change: `refactor-automatic-routing-plan-full-comet`
Status: 已实现，并随 `openspec/changes/archive/2026-05-27-refactor-automatic-routing-plan-full-comet/` 归档。

## 背景

用户要求按照完整 `/comet` 重构 `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md` 并提交本地 Git。上一次处理是 Comet tweak，因此本次设计把 traceability 升级为 full workflow，同时不改变 runtime 行为。

## 选定方案

采用 documentation-only full Comet workflow，并做有边界的结构化编辑：

- 保留既有 automatic orchestration policy 内容。
- 在中文计划中补充 full Comet framing、artifact path 和 evidence boundary。
- 同步更新英文 companion 的高层说明，避免双语漂移。
- 创建 OpenSpec 与 Superpowers 工件，方便后续审计为什么做了这次重构。
- 记录 `bash_unavailable_in_current_windows_shell`，不声称 Comet shell guard transition 已运行。

## 替代方案

1. 再做 tweak 级清理：拒绝，因为用户明确要求完整 `/comet`。
2. 从头重写整份长计划：拒绝，因为容易引入不必要的 policy drift。
3. 有边界的 full workflow 文档重构：采纳，因为它满足 traceability，同时保留稳定 policy 内容。

## 范围

范围内：中文目标实施计划、英文 companion 高层对齐、OpenSpec 工件、Superpowers 设计与实施计划、验证与归档证据。

范围外：Phase 4 checker 实现、runtime worker 或 team 启动、用户级资产修改、本地 main 合入或远端发布。

## 验收

- 中文计划说明本次是 full Comet 文档重构，而不是 tweak。
- 计划列出 full Comet 工件路径。
- 英文 companion 有匹配的高层 framing。
- 提交前记录验证结果。
- 最终报告区分文档证据与 runtime evidence。
