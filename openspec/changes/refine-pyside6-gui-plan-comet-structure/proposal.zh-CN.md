## 为什么

`pyside6_cross_project_gui_capability_plan.*` 已经记录共享 PySide6 runtime 策略，但结构早于新版可执行 Comet 方案族。它需要与 Pi sidecar 方案和 Comet runtime 方案一致的清晰边界：状态解释、关系模型、显式门禁、source-of-truth 图、JSON contract、实施清单、本地集成顺序和诚实验证证据。

## 变更内容

- 将 PySide6 跨项目 GUI 能力双语方案重构为完整 Comet 可执行方案结构。
- 保留共享 runtime 默认路径、本地-only runtime 规则、消费项目所有权模型，以及 override、可见 GUI、打包的显式触发门。
- 为本次文档重构新增 Comet/OpenSpec 支持包和 Superpowers design / implementation 记录。
- 明确当前 change 不安装 PySide6、不写消费项目、不启动可见 GUI、不打包、不做远端发布。

## 能力

### 新增能力

- `pyside6-cross-project-gui-plan-contract`：约束 PySide6 跨项目 GUI 方案必须区分共享 runtime readiness、消费项目 GUI readiness、高影响显式触发门和本地 main 优先发布边界。

### 修改能力

- 无。本变更新增 plan-contract active change，并重写实施方案对。

## 影响

- 影响文档：`docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md` 与 `.zh-CN.md`。
- 影响 OpenSpec artifact：`openspec/changes/refine-pyside6-gui-plan-comet-structure/`。
- 影响 Superpowers artifact：`docs/superpowers/specs/2026-05-27-pyside6-gui-plan-comet-design.md` 与 `docs/superpowers/plans/2026-05-27-refine-pyside6-gui-plan-comet-structure.md`。
- 不执行 runtime 代码变更、依赖安装、目标项目写入、可见 GUI 启动、可执行文件打包、GitLab/GitHub 发布或用户级配置变更。

## 治理字段

- `impact_scope`：文档方案和 active OpenSpec/Superpowers artifact。
- `explicit_non_goals`：PySide6 安装、目标项目写入、可见 GUI、打包、用户级配置变更、远端发布。
- `rollout_sequence`：feature worktree -> 文档重写 -> 本地验证 -> feature 分支提交 -> local CI/MR review -> 本地 main 集成。
- `rollback_plan`：revert feature 分支提交，或把本地 `main` 重置到 merge 前 backup ref。
- `validation_path`：`git diff --check`、`openspec validate`、implementation-plan checker、precommit update/archive gate、OpenSpec guard、local gate、local MR review。
