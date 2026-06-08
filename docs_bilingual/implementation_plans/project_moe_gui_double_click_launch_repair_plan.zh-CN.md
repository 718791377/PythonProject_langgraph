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

- 状态：因无参 launcher 真实验证发现第三个根因，重新打开一个本地 hotfix 切片。
- 前两轮本地完成状态仍然有效：B 方案包 `662c2de`、B 运行时/helper 包 `c66209e`、A 受管产物刷新 `0c3b49d`。
- 2026-06-03 发现的新增根因：daemon 父进程会先在目标项目写入 `tools/project_moe_gui/project_moe_gui.daemon.log`，随后子进程执行 Phase 1 readiness preflight 时看到 A 已出现未跟踪文件，可能返回 `blocked:dirty_target_project`，导致 GUI 子进程在显示窗口前退出。
- 重新打开切片的源头规则：daemon log 与 lock 运行时产物必须写入目标项目已忽略的 `.project-runtime/project_moe_gui/` 目录，不能写入受管安装目录 `tools/project_moe_gui/`。
- 本 docs_bilingual 包是重新打开的 B 源码 hotfix 的治理包；它合入 B 本地 `main` 后，代码分支可通过 Stage A receipt/claim 引用该治理包。
- 远端发布仍不在范围内，未执行。

<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->

- [x] 复现并归类最初的目标 launcher 症状。
- [x] 确认目标 preflight 仍可通过共享 runtime 执行。
- [x] 确认显式启用时 visible-launch dry-run 成功。
- [x] 记录两包修复方案，并从父级 MOE GUI toolchain 方案交叉引用。
- [x] 将方案文档包合入 B 本地 `main`。
- [x] 在 B 实施共享 runtime helper 与 launcher-refresh 修复。
- [x] 验证第一轮 B toolchain 测试、共享 runtime 检查、OpenSpec guard、本地 gate 与本地 MR review。
- [x] 从 B 刷新第一轮 A 的受管 Project MOE GUI 安装产物。
- [x] 验证第一轮 A preflight、visible dry-run 与既有 thesis MOE 测试。
- [x] 提交并合入第一轮 A 本地 `main`。
- [x] 保留第一轮 A 本地 rollback evidence 与 completed receipt。
- [x] 清理第一轮已集成的 A feature worktree 与本地 feature branch。
- [x] 复现重新打开的无参 launcher 失败，并识别第三根因：daemon 诊断日志创建会在 Phase 1 readiness 前污染 A。
- [x] 在代码实施前，把第三根因治理更新记录到本 active implementation plan。
- [ ] 将第三根因治理包合入 B 本地 `main`。
- [ ] 更新 B daemon/toolchain 源码，使 daemon log 与 lock 路径生成到 `.project-runtime/project_moe_gui/`。
- [ ] 新增或更新 B 回归测试：如果生成的 daemon log/lock 路径指向受管 `tools/project_moe_gui/`，测试必须失败。
- [ ] 验证 B hotfix 测试、py_compile、diff hygiene、precommit update/archive、本地 gate 与本地 MR review。
- [ ] 将 B 源码 hotfix 合入本地 `main`，并通过受保护 helper 清理 feature worktree/branch。
- [ ] 从更新后的 B 本地 `main` 刷新 A 的受管 Project MOE GUI 产物。
- [ ] 如存在旧残留日志 `D:\PythonProject_paper_suggest\tools\project_moe_gui\project_moe_gui.daemon.log`，先删除它。
- [ ] 用 `PROJECT_MOE_GUI_VISIBLE_SMOKE_EXIT_MS` 验证 A 无参 `project-moe-gui.cmd` 启动，并确认诊断日志写到 `.project-runtime/project_moe_gui/` 且不污染 A。
- [ ] 重跑 A preflight、visible dry-run、thesis MOE 测试、本地 gate 与本地 MR review。
- [ ] 提交并合入刷新后的 A 受管产物到 A 本地 `main`。

<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->

- B 方案文档包本地 main commit：`662c2de`（文档：记录 MOE GUI 双击启动修复方案）。
- B 运行时/helper 实现包本地 main commit：`c66209e`（修复：补齐 MOE GUI 双击启动运行时）。
- A 受管安装产物刷新本地 main commit：`0c3b49d861b8fd0ae7e6bf9f81405bca48f56f2a`。
- A 回滚 ref：`refs/backup/local-main/20260603-083632-before-project-moe-gui-double-click-refresh` -> `958f003a0a82dc2c15ecb8ca6fe4b263efbfdd02`。
- A completed receipt：`D:\PythonProject_paper_suggest\.omx\session-claims\paper-suggest-project-moe-gui-double-click-refresh-20260603.json`。
- 第一轮 A preflight 验证命令：`cmd /c "D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json"` 返回 exit 0，且包含 `ok: true`、`token: ok`、`launcher_runtime_reexec: true`、`qfluentwidgets_status.ok: true`、`phase1_readiness_gate.readiness_status: ready`。
- 第一轮 A visible dry-run 验证命令：`cmd /c "set PROJECT_MOE_GUI_DRY_RUN_VISIBLE=1&& D:\PythonProject_paper_suggest\project-moe-gui.cmd --allow-visible --json"` 返回 exit 0，且包含 `ok: true`、`token: ok`、`message: Visible GUI launch dry-run passed.`。
- 第一轮 A 回归验证命令：`python -m unittest discover -s test -p "test_thesis_moe_mode.py"` 返回 `Ran 6 tests` 与 `OK`。
- 重新打开失败证据：真实无参目标启动会写入 `D:\PythonProject_paper_suggest\tools\project_moe_gui\project_moe_gui.daemon.log`；该路径未被忽略，因此 A 会在子进程 readiness preflight 前变脏。
- 重新打开阻塞证据：daemon 创建的日志存在时，子进程启动可能报告 `blocked:dirty_target_project`。
- 重新打开后的必需验收证据：hotfix 后 daemon diagnostics 与 lock 必须位于 `D:\PythonProject_paper_suggest\.project-runtime\project_moe_gui\`，且 `git -C D:\PythonProject_paper_suggest status --short` 不得显示 daemon 生成文件。
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
- 重新打开的证据显示：daemon 在 `tools/project_moe_gui/` 下生成诊断日志会在 Phase 1 readiness 前污染 A，因此 daemon 运行时产物目录必须迁移到已忽略的 `.project-runtime/project_moe_gui/`。

## 实施变更

- 在 B 中让共享 runtime helper 对既有 requirements 做模板合并；缺失 `qfluentwidgets` 时 `verify/provision` 必须 fail closed。
- 在 B 中保持无参人工 launcher 走 daemon：父 CMD 可以退出，子进程用配置的共享 runtime 启动可见 GUI；`--preflight --json` 继续以前台机器可读方式执行。
- 在 B 中把 daemon log 与 lock 路径生成到目标项目已忽略的 `.project-runtime/project_moe_gui/` 目录，确保 launcher 诊断不会污染 `tools/project_moe_gui/` 下的受管安装产物。
- 在 B 中保持 `--json` 未带 `--preflight` 时机器安全，不得误打开可见窗口。
- 在 A 中只更新 B 管理的 Project MOE GUI 产物：`project-moe-gui.cmd`、`tools/project_moe_gui/launcher.py`、config、manifest、README。
- 不在 A 安装 PySide6；继续使用 `D:\PythonProject_langgraph\.shared_runtimes\pyside6`。

## 验证计划

B 仓库：

- `python test/project_moe_gui_toolchain.test.py` - 验证生成的 MOE GUI 受管 launcher、daemon plan、安装产物行为，以及 daemon 运行时产物必须位于 `.project-runtime/project_moe_gui/`。
- `python test/check_pyside6_shared_runtime_contract.test.py` - verifies the shared PySide6 runtime contract checker behavior.
- `python tools/check_pyside6_shared_runtime_contract.py --root . --json` - checks shared runtime readiness and dependency evidence in machine-readable form.
- `python tools/run_openspec_guard.py --root .` - validates repository OpenSpec and governance guard health.
- `tools/ci/local_gate.ps1` - runs the shared local CI gate used before local integration and remote CI.
- `tools/ci/local_mr_review.ps1` - runs local MR review before local `main` integration.

A 仓库：

- `cmd /c "D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json"` - 验证目标项目 launcher preflight，不打开可见 GUI。历史 `blocked:invalid_session_record` 只允许在存在 `view_model` 时作为诊断 banner；清理旧日志后不得出现 `blocked:dirty_target_project`。
- `cmd /c "set PROJECT_MOE_GUI_DRY_RUN_VISIBLE=1&& D:\PythonProject_paper_suggest\project-moe-gui.cmd --allow-visible --json"` - verifies explicit visible-launch dry-run behavior without entering the Qt event loop.
- `python -m unittest discover -s test -p "test_thesis_moe_mode.py"` - checks existing thesis MOE mode regression coverage in A.
- 无参启动 smoke：设置 `PROJECT_MOE_GUI_VISIBLE_SMOKE_EXIT_MS=500`，运行 `D:\PythonProject_paper_suggest\project-moe-gui.cmd`，随后检查 `.project-runtime/project_moe_gui/project_moe_gui.daemon.log`；父 CMD 可以退出，子进程 smoke 必须干净退出，且 A 除已忽略的 `.project-runtime/` 外必须保持干净。
- 仅在显式允许交互时做双击验收：双击 `project-moe-gui.cmd` 后父 CMD 可以退出，但 GUI 窗口必须出现，或保留稳定诊断路径。

## 假设

- 已选择提交范围：B 与 A 都提交。
- 当前实施请求与 local-main-first 规则授权本地 `main` 合入；不授权远端发布。
- QFluentWidgets 当前仅批准本地开发使用；商业重分发或打包前需要单独许可证审查。
