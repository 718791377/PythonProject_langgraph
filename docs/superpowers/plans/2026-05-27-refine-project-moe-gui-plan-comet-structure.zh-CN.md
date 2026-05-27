---
change: refine-project-moe-gui-plan-comet-structure
design-doc: docs/superpowers/specs/2026-05-27-project-moe-gui-plan-comet-design.zh-CN.md
base-ref: 9fbc66e
---

# 重构 Project MOE GUI 计划 Comet 结构实施计划

> **给 agentic workers：** 本变更是文档/治理重构，优先使用 `$comet` 控制层和 `superpowers:executing-plans` 的逐项执行方式。所有事项使用 checkbox 跟踪；不得把未运行的 Comet bash 脚本声明为通过。

**目标：** 将 Project MOE Agent GUI 实施方案重构成完整 `/comet` 可追溯的可执行方案结构，并与新版 Pi sidecar 方案和 Comet runtime 敏捷关注领域方案保持同级颗粒度。

**范围：** 只修改实施方案与本 change 的 OpenSpec / Superpowers 支撑 artifacts；不安装 PySide6，不写目标项目，不改 user-level 目录，不进行远端发布。

---

## Step 1：确认现有 Comet / OpenSpec change

- [x] 复用 `openspec/changes/refine-project-moe-gui-plan-comet-structure/`。
- [x] 确认 `.comet.yaml` 处于 `phase: verify` 且记录 `comet_script_state: blocked:bash_not_found_on_windows`。
- [x] 确认本次不是 runtime 代码实现，而是计划结构和证据收口。

## Step 2：重构目标方案结构

- [x] 将英文主版 `project_moe_agent_gui_toolchain_plan.md` 更新为完整 Comet 结构。
- [x] 将中文对照版 `project_moe_agent_gui_toolchain_plan.zh-CN.md` 同步更新。
- [x] 保留 `status: draft`，用 `plan_readiness` 表示可以进入实现切片。
- [x] 对齐 Pi sidecar 方案结构：复核结论、关系模型、目标/非目标、运行时架构、source of truth、安装产物、CLI/JSON/state contract、readiness gates、rollback、风险和自检。
- [x] 对齐 Comet runtime 方案语义：management record、phase gates、Monitoring return、implementation slices、file ownership map、local integration order 与 evidence retention。

## Step 3：修复支撑 artifacts

- [x] 修复 `tasks.zh-CN.md` 的乱码/问号占位。
- [x] 修复 `design.zh-CN.md` 的乱码/问号占位。
- [x] 修复本 Superpowers 中文设计文档。
- [x] 修复本 Superpowers 中文实施计划。
- [x] 修复中文 management record。

## Step 4：验证

- [x] 运行 `git diff --check`。
- [x] 运行 `openspec validate refine-project-moe-gui-plan-comet-structure --strict`。
- [x] 运行 `python .\tools\check_implementation_plan_rules.py --root . --json`。
- [x] 运行 `python .\tools\check_precommit_update_archive.py --root . --json`。
- [x] 运行 `python .\tools\run_openspec_guard.py --root .`。

## Step 5：提交与本地集成

- [ ] 用中文提交信息提交 feature 分支。
- [ ] commit 后运行 `.\tools\ci\local_gate.ps1`。
- [ ] commit 后运行 `.\tools\ci\local_mr_review.ps1`。
- [ ] 经用户已授权的本地集成流程合入本地 `main`。
- [ ] 合入后确认主目录 HEAD 等于本地 `main`。

## 非目标

- [ ] 不推送 GitLab / GitHub。
- [ ] 不打开或合并远端 MR。
- [ ] 不写入 `D:\PythonProject_paper_suggest`。
- [ ] 不把 `D:\PythonProject_paper_suggest` 标记为 GUI ready。
