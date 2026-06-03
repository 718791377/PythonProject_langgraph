---
doc_id: project_moe_gui_double_click_launch_repair_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/project_moe_gui_double_click_launch_repair_plan.md
created_at: 2026-06-02
updated_at: 2026-06-03
related_docs:
  - docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md
  - docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.zh-CN.md
---

# Project MOE GUI 双击启动修复方案

## 摘要

本方案修复目标项目 `D:\PythonProject_paper_suggest\project-moe-gui.cmd` 双击后 CMD 窗口退出，但 GUI 窗口没有保持可见的问题。

修复分为两个 local-main-first 包：

1. 先在 `D:\PythonProject_langgraph` 记录本方案并合入本地 `main`。
2. 再在 `D:\PythonProject_langgraph` 实施持久化修复，并把安装产物更新到 `D:\PythonProject_paper_suggest`，随后分别合入两个仓库的本地 `main`。

除非后续用户明确要求 GitLab/GitHub 发布，否则本方案不包含远端推送。

## Current Status

<!-- CURRENT_STATUS_START -->

- 状态：已完成本地落地。
- B（`D:\PythonProject_langgraph`）方案文档包已合入本地 `main`：`662c2de`。
- B 运行时/helper 实现包已合入本地 `main`：`c66209e`。
- A（`D:\PythonProject_paper_suggest`）受管安装产物刷新已合入本地 `main`：`0c3b49d`。
- A 回滚 ref：`refs/backup/local-main/20260603-083632-before-project-moe-gui-double-click-refresh` -> `958f003`。
- A feature worktree 与本地 feature branch 已在本地 main 合入后清理。
- 远端发布仍不在本方案范围内，本轮没有推送 GitLab/GitHub。

<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->

- [x] 复现并归类目标 launcher 症状。
- [x] 确认目标 preflight 仍可通过共享 runtime 成功执行。
- [x] 确认显式启用时 visible-launch dry-run 成功。
- [x] 记录两包修复方案，并从父级 MOE GUI toolchain 方案交叉引用。
- [x] 将方案文档包合入 B 本地 `main`。
- [x] 在 B 实施共享 runtime helper 与 launcher-refresh 修复。
- [x] 验证 B toolchain 测试、共享 runtime 检查、OpenSpec guard、本地 gate 与本地 MR review。
- [x] 从 B 刷新 A 的受管 Project MOE GUI 安装产物。
- [x] 验证 A preflight、visible dry-run 与既有 thesis MOE 测试。
- [x] 提交并合入 A 本地 `main`。
- [x] 保留 A 本地 rollback evidence 与 completed receipt。
- [x] 清理已集成的 A feature worktree 与本地 feature branch。

<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->

- B 方案文档包本地 main commit：`662c2de`（`文档：记录 MOE GUI 双击启动修复方案`）。
- B 运行时/helper 实现包本地 main commit：`c66209e`（`修复：补齐 MOE GUI 双击启动运行时`）。
- A 受管安装产物刷新本地 main commit：`0c3b49d861b8fd0ae7e6bf9f81405bca48f56f2a`。
- A 回滚 ref：`refs/backup/local-main/20260603-083632-before-project-moe-gui-double-click-refresh` -> `958f003a0a82dc2c15ecb8ca6fe4b263efbfdd02`。
- A completed receipt：`D:\PythonProject_paper_suggest\.omx\session-claims\paper-suggest-project-moe-gui-double-click-refresh-20260603.json`。
- A preflight 验证命令：`cmd /c "D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json"` 返回 exit 0，且包含 `ok: true`、`token: ok`、`launcher_runtime_reexec: true`、`qfluentwidgets_status.ok: true`、`phase1_readiness_gate.readiness_status: ready`。
- A visible dry-run 验证命令：`cmd /c "set PROJECT_MOE_GUI_DRY_RUN_VISIBLE=1&& D:\PythonProject_paper_suggest\project-moe-gui.cmd --allow-visible --json"` 返回 exit 0，且包含 `ok: true`、`token: ok`、`message: Visible GUI launch dry-run passed.`。
- A 回归验证命令：`python -m unittest discover -s test -p "test_thesis_moe_mode.py"` 返回 `Ran 6 tests` 与 `OK`。
- B 源码面：`tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py` 与 `tools/project_moe_gui_toolchain/src/project_moe_gui/daemon.py`。
- 共享 runtime helper 面：`tools/pyside6_gui_helpers/ensure-shared-pyside6-runtime.ps1`。
- 远端发布证据：未授权，未执行。

<!-- EVIDENCE_INDEX_END -->

## 当前证据

- 目标 launcher 位于 `D:\PythonProject_paper_suggest\project-moe-gui.cmd`，当前以前台方式调用 `python tools\project_moe_gui\launcher.py`。
- `--preflight --json` 已返回 `token=ok`、`launcher_runtime_reexec=true` 和 Ready Lane Phase 1 证据。
- `PROJECT_MOE_GUI_DRY_RUN_VISIBLE=1` 的可见启动 dry-run 已返回成功。
- 本机共享 PySide6 runtime 经维护后已可 import PySide6 与 QFluentWidgets；但共享 runtime helper 仍需把 `PySide6-Fluent-Widgets` 回填到旧的 `requirements-pyside6.txt`。
- B 的 toolchain 源码已经包含 daemon / 无 CMD 常驻设计，但 A 的已安装 managed artifacts 可能落后，需要从 B 重新刷新。

## 实施变更

- 在 B 中让共享 runtime helper 对既有 requirements 做模板合并；缺失 `qfluentwidgets` 时 `verify/provision` 必须 fail closed。
- 在 B 中保持无参人工 launcher 走 daemon：父 CMD 可以退出，子进程用配置的共享 runtime 启动可见 GUI；`--preflight --json` 继续以前台机器可读方式执行。
- 在 B 中保持 `--json` 未带 `--preflight` 时机器安全，不得误打开可见窗口。
- 在 A 中只更新 B 管理的 Project MOE GUI 产物：`project-moe-gui.cmd`、`tools/project_moe_gui/launcher.py`、config、manifest、README。
- 不在 A 安装 PySide6；继续使用 `D:\PythonProject_langgraph\.shared_runtimes\pyside6`。

## 验证计划

B 仓库：

- `python test/project_moe_gui_toolchain.test.py` - verifies generated MOE GUI managed launcher, daemon plan, and install artifact behavior.
- `python test/check_pyside6_shared_runtime_contract.test.py` - verifies the shared PySide6 runtime contract checker behavior.
- `python tools/check_pyside6_shared_runtime_contract.py --root . --json` - checks shared runtime readiness and dependency evidence in machine-readable form.
- `python tools/run_openspec_guard.py --root .` - validates repository OpenSpec and governance guard health.
- `tools/ci/local_gate.ps1` - runs the shared local CI gate used before local integration and remote CI.
- `tools/ci/local_mr_review.ps1` - runs local MR review before local `main` integration.

A 仓库：

- `cmd /c "D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json"` - verifies target-project launcher preflight without opening a visible GUI.
- `cmd /c "set PROJECT_MOE_GUI_DRY_RUN_VISIBLE=1&& D:\PythonProject_paper_suggest\project-moe-gui.cmd --allow-visible --json"` - verifies explicit visible-launch dry-run behavior without entering the Qt event loop.
- `python -m unittest discover -s test -p "test_thesis_moe_mode.py"` - checks existing thesis MOE mode regression coverage in A.
- 仅在显式允许交互时做双击验收：双击 `project-moe-gui.cmd` 后父 CMD 可以退出，但 GUI 窗口必须出现，或保留稳定诊断路径。

## 假设

- 已选择提交范围：B 与 A 都提交。
- 当前实施请求与 local-main-first 规则授权本地 `main` 合入；不授权远端发布。
- QFluentWidgets 当前仅批准本地开发使用；商业重分发或打包前需要单独许可证审查。
