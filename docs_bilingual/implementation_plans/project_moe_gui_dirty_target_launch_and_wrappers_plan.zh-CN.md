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

- Closeout update: B governance plan package is on local `main` at `5bfec68`.
- Closeout update: B runtime repair package is on local `main` at `5d2deff`; Project MOE GUI is upgraded from `0.2.44` to `0.2.45`.
- Closeout update: B rollback ref is `refs/backup/local-main/20260613-154650-before-fix-moe-gui-dirty-launch-wrapper-runtime`.
- Closeout update: runtime feature worktree/branch `fix-moe-gui-dirty-launch-wrapper-runtime` has been cleaned after local-main integration.
- Closeout update: A managed Project MOE GUI artifacts are installed and committed on A local `main` at `a22a13b`.
- Closeout update: A `project-moe-gui.cmd --preflight --json` returns `ok=true`, a usable `view_model`, and no blockers.
- Closeout update: A `project-status --json` returns `ok=true`, `enabled=true`, `effective_enabled=true`, branch `main`, and 5 valid registered sessions.
- Closeout update: `thesis-moe-off.cmd` and `thesis-moe-on.cmd` were live-verified as project-default off/on wrappers; final project-default MOE state was restored to `enabled`.
- Closeout update: Spec Kit authority guard now excludes ignored `.tmp/` scratch output, so `.tmp/skills-usage-audit-*.json` does not block unrelated local commits.
- Remote publication remains unauthorized and not performed.

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
- [x] 合入本方案到 B 本地 `main`。
- [x] 创建 B runtime feature worktree，并补 receipt 与 claim。
- [x] 提升 Project MOE GUI toolchain patch 版本。
- [x] 将 dirty-target 下普通 GUI preflight、read、write 从 fatal blocker 改成 warning。
- [x] 补充或更新 B 测试：dirty-target preflight、dirty-target MOE 状态写入、launcher Python 选择、project-default wrappers。
- [x] 运行 B 定向测试、precommit update/archive、local gate、local MR review。
- [x] 合入 B runtime 修复到本地 `main`，并清理 feature worktree 与 branch。
- [x] 创建或复用 A 项目的干净 `main` worktree，绕开 dirty A 主目录。
- [x] 从 B 本地 `main` 安装刷新后的 Project MOE GUI 受管产物到干净 A worktree。
- [x] 验证 A preflight、新增 session 发现、无参启动路径、silent VBS 契约、thesis on/off wrappers。
- [x] 提交并合入 A 受管产物刷新到 A 本地 `main`。
- [x] 保持 dirty A 主目录不被本切片修改，并把它作为单独后续清理项汇报。
- [x] Close the Spec Kit guard false positive: ignored `.tmp` skills-audit JSON must not block unrelated local commits.

<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->

- B governance package: `5bfec68`.
- B runtime package: `5d2deff`.
- B rollback ref: `refs/backup/local-main/20260613-154650-before-fix-moe-gui-dirty-launch-wrapper-runtime`.
- B completed claim: `.omx/session-claims/completed/fix-moe-gui-dirty-launch-wrapper-runtime.json`.
- B runtime source surfaces: `tools/project_moe_gui_toolchain/src/project_moe_gui/__init__.py`, `tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py`, `test/project_moe_gui_toolchain.test.py`.
- B closeout guard surfaces: `tools/check_spec_kit_authority_guard.py`, `test/spec_kit_authority_guard.test.py`, and this bilingual plan pair.
- B runtime targeted tests passed for dirty-target preflight, dirty-target managed namespace write allowance, runtime Python launcher selection, and project-default thesis wrappers.
- B runtime full Python unittest evidence passed with 814 tests.
- B runtime OpenSpec guard evidence passed with 66/66 checks.
- B runtime local MR review evidence passed.
- Earlier full `tools/ci/local_gate.ps1` wrapper run hit a transient order-sensitive failure and must not be cited as green; closeout uses fresh split verification evidence.
- A managed-artifact refresh commit: `a22a13b`.
- A update dry-run after install returned `status=up_to_date`, `no_op=true`, and no blockers.
- A `project-moe-gui.cmd --preflight --json` returned `ok=true`, a usable `view_model`, and no blockers.
- A `project-status --json` returned `ok=true`, `enabled=true`, `effective_enabled=true`, branch `main`, and 5 valid registered sessions.
- A `thesis-moe-off.cmd` and `thesis-moe-on.cmd` live verification switched project-default MOE off and back on; final state restored to `enabled`.
- Closeout guard evidence: `python test/spec_kit_authority_guard.test.py` covers `.tmp/skills-usage-audit-7d.json` exclusion, and `python tools/check_spec_kit_authority_guard.py --root . --json` reports zero findings even when ignored `.tmp` audit output exists.
- Remote publication evidence: not authorized and not performed.

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