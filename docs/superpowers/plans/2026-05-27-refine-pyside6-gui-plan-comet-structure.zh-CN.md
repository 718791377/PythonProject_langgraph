---
change: refine-pyside6-gui-plan-comet-structure
design-doc: docs/superpowers/specs/2026-05-27-pyside6-gui-plan-comet-design.md
base-ref: 8a4aee5
---

# 重构 PySide6 GUI 方案 Comet 结构实施计划

> **For agentic workers:** 使用 `$comet` 和 `superpowers:executing-plans` 风格执行。本次仅是文档/治理重构。不得安装 PySide6、写消费项目、启动可见 GUI、打包可执行文件或推送远端 ref。

**目标：** 将 PySide6 跨项目 GUI 能力实施方案重写为完整 `/comet` 可追踪的可执行方案结构，并对齐 Pi sidecar 与 Comet runtime 方案族。

## Step 1：确认 change 范围

- [x] 使用专用 feature worktree。
- [x] 创建 OpenSpec change `refine-pyside6-gui-plan-comet-structure`。
- [x] 在 `.comet.yaml` 记录 `comet_script_state: blocked:bash_not_found_on_windows`。
- [x] 确认本 change 仅限文档/OpenSpec。

## Step 2：重构目标方案

- [x] 更新英文主方案。
- [x] 更新中文配套方案。
- [x] 保留 PySide6 特定事实和显式触发门。
- [x] 对齐 Pi sidecar 与 Comet runtime 方案结构。

## Step 3：验证

- [ ] 运行 `git diff --check`。
- [ ] 运行 `openspec validate refine-pyside6-gui-plan-comet-structure --strict`。
- [ ] 运行 `python .\tools\check_implementation_plan_rules.py --root . --json`。
- [ ] 运行 `python .\tools\check_precommit_update_archive.py --root . --json`。
- [ ] 运行 `python .\tools\run_openspec_guard.py --root .`。

## Step 4：提交并本地集成

- [x] 使用中文提交信息提交。
- [x] 运行 local gate。
- [x] 运行 local MR review。
- [ ] 创建本地 main rollback backup ref。
- [ ] fast-forward 合入本地 `main`。
- [ ] 保留 completed receipt/claim 并清理已集成 worktree。

## 非目标

- [ ] 不推送 GitLab/GitHub。
- [ ] 不打开或合并远端 MR。
- [ ] 不安装 PySide6。
- [ ] 不写消费项目。
- [ ] 不启动可见 GUI 或打包可执行文件。
