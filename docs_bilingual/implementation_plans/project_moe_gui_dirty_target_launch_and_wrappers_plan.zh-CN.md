---
doc_id: project_moe_gui_dirty_target_launch_and_wrappers_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/project_moe_gui_dirty_target_launch_and_wrappers_plan.md
created_at: 2026-06-13
updated_at: 2026-06-13
related_docs:
  - docs_bilingual/implementation_plans/project_moe_gui_double_click_launch_repair_plan.zh-CN.md
---

# Project MOE GUI dirty target 启动与 thesis wrapper 修复方案

## 摘要

本方案修复目标项目在新增 Codex session 或存在无关 dirty 文件后，`project-moe-gui.cmd` 与 `project-moe-gui-silent.vbs` 双击启动提前退出且没有 GUI 窗口的问题；同时按照现有 Project MOE 镜头契约刷新 `thesis-moe-on.cmd` 与 `thesis-moe-off.cmd`。

除非后续用户明确要求 GitLab 或 GitHub 发布，否则本方案不包含远端推送、MR、合并或镜像同步。

## 当前状态

<!-- CURRENT_STATUS_START -->

- B 源仓库是 `D:\PythonProject_langgraph`，负责维护 Project MOE GUI toolchain。
- A 目标项目是 `D:\PythonProject_paper_suggest`；当前主目录位于 dirty 分支 `implement-r6-live-runtime`，因此不能作为本次最终安装或提交面。
- 本次 A 受管产物刷新必须使用干净的 A 项目 `main` worktree 完成最终安装、验证与本地提交。
- 现有 A launcher 仍可能依赖 ambient `python`；修复后的启动路径应优先使用配置的共享 PySide6 runtime Python。
- 现有 preflight 可能把 `blocked:dirty_target_project` 当成 fatal，并返回没有可用 `view_model` 的结果；普通 GUI 启动、读取与写入应返回可用 view model 和诊断信息。
- 本切片用户决策：无关 dirty target 状态只允许作为普通 GUI 读写的 diagnostics 或 warnings；安装、更新、受管文件覆盖和本地提交仍必须使用干净 A worktree。
- 本切片用户决策：`thesis-moe-on.cmd` 与 `thesis-moe-off.cmd` 保持项目默认 MOE 开关语义，不写死显式 lens 或 category 列表。

<!-- CURRENT_STATUS_END -->

## 实施变更

- 在 B 中保持安装与更新安全门禁严格，但普通 preflight、session discovery、MOE 状态读取和写入遇到无关 dirty target 时，降级为诊断 warning。
- 在 B 中确保只要 GUI runtime 自身可运行，preflight 即使看到目标项目无关 dirty 文件，也必须返回可用 `view_model`。
- 在 B 中所有 MOE 状态写入仍只能通过目标项目 Phase 1 CLI，且只允许写入受管 MOE 状态面；不得修改或清理无关 dirty 文件。
- 在 B 中更新 launcher 生成逻辑，使 `project-moe-gui.cmd` 优先使用配置的共享 runtime Python，`project-moe-gui-silent.vbs` 继续委托已修复 cmd 并保留诊断路径。
- 在 B 中更新 wrapper 生成逻辑，使 `thesis-moe-on.cmd` 与 `thesis-moe-off.cmd` 调用当前 Phase 1 CLI 的 project-default on/off 契约。
- 在 A 中只把 B 受管的 Project MOE GUI 产物安装到干净 A `main` worktree；不向 A 安装 PySide6，不复制私有 `MOE.md` 正文。

## 任务清单

<!-- TASK_BACKLOG_START -->

- [x] 确认当前 A 主目录 dirty，不能作为本次最终提交面。
- [x] 在本方案中冻结 dirty-target 与 wrapper 决策。
- [ ] 合入本方案到 B 本地 `main`。
- [ ] 创建 B runtime feature worktree，并补 receipt 与 claim。
- [ ] 提升 Project MOE GUI toolchain patch 版本。
- [ ] 将 dirty-target 下普通 GUI preflight、read、write 从 fatal blocker 改成 warning。
- [ ] 补充或更新 B 测试：dirty-target preflight、dirty-target MOE 状态写入、launcher Python 选择、project-default wrappers。
- [ ] 运行 B 定向测试、precommit update/archive、local gate、local MR review。
- [ ] 合入 B runtime 修复到本地 `main`，并清理 feature worktree 与 branch。
- [ ] 创建或复用 A 项目的干净 `main` worktree，绕开 dirty A 主目录。
- [ ] 从 B 本地 `main` 安装刷新后的 Project MOE GUI 受管产物到干净 A worktree。
- [ ] 验证 A preflight、新增 session 发现、无参启动路径、silent VBS 契约、thesis on/off wrappers。
- [ ] 提交并合入 A 受管产物刷新到 A 本地 `main`。
- [ ] 保持 dirty A 主目录不被本切片修改，并把它作为单独后续清理项汇报。

<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->

- A 状态证据：`D:\PythonProject_paper_suggest` 主目录位于 dirty 分支 `implement-r6-live-runtime`，不是本次最终提交面。
- B runtime 后续源码面：`tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py`、`daemon.py`、`gui_shell.py` 以及 Project MOE installer 与 updater 脚本。
- A 受管 launcher 后续面：`project-moe-gui.cmd`、`project-moe-gui-silent.vbs`、`thesis-moe-on.cmd`、`thesis-moe-off.cmd` 与 `tools/project_moe_gui/`。
- 预期验证证据：dirty target preflight 返回带诊断的可用 view model；wrapper 命令保留项目默认语义；最终 A 安装从干净 A `main` worktree 提交。
- 远端发布证据：未授权，未执行。

<!-- EVIDENCE_INDEX_END -->

## 验证计划

B 仓库：

- `python test/project_moe_gui_toolchain.test.py` 验证生成 launcher、wrapper 行为与 dirty-target 处理。
- dirty target fixture 必须返回可用 GUI preflight 数据，而不是没有 view model 的 fatal 结果。
- dirty target 写入 fixture 只能通过 Phase 1 CLI 更新 MOE 状态，不得改动无关 dirty 文件。
- launcher/template 测试必须确认共享 runtime Python 选择和 hidden-launch diagnostics。
- wrapper 测试必须确认 `thesis-moe-on/off` 是 project-default 语义，未写死显式 lens 或 category 列表。
- 本地集成前必须通过 `python tools/check_precommit_update_archive.py --root . --json`、`tools/ci/local_gate.ps1` 与 `tools/ci/local_mr_review.ps1`。

A 干净 main worktree：

- `project-moe-gui.cmd --preflight --json` 返回 `ok` 或带 warning 但有可用 `view_model` 的结果；普通 GUI 启动不得因 `blocked:dirty_target_project` fatal 退出。
- 新增或发现 Codex session 后，`project-moe-gui.cmd` 与 `project-moe-gui-silent.vbs` 不得闪退且无诊断。
- `thesis-moe-on.cmd` 与 `thesis-moe-off.cmd` 返回 JSON，并能切换项目默认 MOE 状态。
- 模拟无关 dirty 文件时，普通 GUI preflight、read、write 允许继续并显示诊断；安装与更新仍保持 clean-worktree-only。

## 假设

- A 主目录中的 dirty 工作是另一个未收口的 A 项目改动，本次不清理。
- dirty-target 放行只限普通 Project MOE GUI 运行，不授权安装或更新覆盖、不授权清理无关文件、不授权从 dirty worktree 提交。
- 现有 MOE lens 与 category 能力保持不删除。