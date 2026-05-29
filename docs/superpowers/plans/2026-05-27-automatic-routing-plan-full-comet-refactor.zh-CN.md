# 自动路由方案完整 Comet 重构实施计划

> **面向 agentic workers：** 本计划采用 inline execution；当前任务是 documentation-only 单切片工作，不满足 durable/persistent team 启动阈值。

**目标：** 通过完整 `/comet` 文档流程重构自动协同路由强制化实施计划，并在本地 feature branch 提交。

**架构：** 保留既有 policy baseline，只在文档与 workflow artifact 层补齐 full Comet traceability。OpenSpec 负责 WHAT，Superpowers 负责 HOW，仓库验证命令负责 acceptance evidence。

**技术栈：** Markdown、OpenSpec CLI、PowerShell、Python repository checkers、本地 CI 脚本。

---

## 文件结构

- 修改 `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md`：中文主目标计划。
- 修改 `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.md`：英文 companion 高层对齐。
- 新建 `openspec/changes/refactor-automatic-routing-plan-full-comet/proposal.md`：变更动机和范围。
- 新建 `openspec/changes/refactor-automatic-routing-plan-full-comet/design.md`：设计决策和替代方案。
- 新建 `openspec/changes/refactor-automatic-routing-plan-full-comet/tasks.md`：完成清单。
- 新建 `openspec/changes/refactor-automatic-routing-plan-full-comet/specs/automatic-orchestration-plan-doc-refactor/spec.md`：delta requirements。
- 新建 `openspec/changes/refactor-automatic-routing-plan-full-comet/management.md`：Comet 管理清单。
- 新建 `openspec/changes/refactor-automatic-routing-plan-full-comet/verification.md`：验证报告。
- 新建 `docs/superpowers/specs/2026-05-27-automatic-routing-plan-full-comet-refactor-design.md`：Superpowers 设计文档。
- 新建 `docs/superpowers/plans/2026-05-27-automatic-routing-plan-full-comet-refactor.md`：实施计划英文主版。

## Task 1: OpenSpec 与 Superpowers 工件

- [x] 创建 full OpenSpec change 目录和 `.openspec.yaml`。
- [x] 写入 proposal、design、tasks、management 和 verification。
- [x] 写入 delta spec。
- [x] 写入 Superpowers design doc 和 implementation plan。

## Task 2: 文档重构

- [x] 更新中文计划 frontmatter version/date。
- [x] 用 full Comet reading path 和 artifact map 替换旧 tweak note。
- [x] 增加 Phase 4 边界说明，明确本次不是 runtime evidence。
- [x] 更新英文 companion 的 high-level framing 与 cold-start/full-Comet 说明。

## Task 3: 验证

- [x] 运行 `git diff --check` 并记录结果。
- [x] 运行 `openspec validate --all` 并记录结果。
- [x] 运行 startup/mojibake 与 canary guards 并记录结果。
- [x] 运行 precommit/archive guard 与 OpenSpec guard 并记录结果。
- [x] 运行 local gate 并记录结果。

## Task 4: 归档与提交

- [x] 验证后用 `openspec archive refactor-automatic-routing-plan-full-comet --skip-specs --yes` 归档。
- [x] 在 `docs/refactor-automatic-routing-plan-comet` 本地提交。
- [x] 提交后运行 local MR review 并报告结果。
