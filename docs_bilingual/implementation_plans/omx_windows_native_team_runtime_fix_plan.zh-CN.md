---
doc_id: omx_windows_native_team_runtime_fix_plan
lang: zh-CN
doc_class: implementation_plan
status: active
translation_of: docs_bilingual/implementation_plans/omx_windows_native_team_runtime_fix_plan.md
change: fix-omx-windows-native-team-runtime-20260618
base_ref: 2d53bd73c8a8b9202d6643fe26985960c7a740a0
---

# OMX Windows 原生团队运行时修复方案

> 面向 agentic worker：用 subagent-driven-development 或 executing-plans 逐项执行。本方案分成 Stage A 与 Stage B 两个 local-main 集成包。不要把当前损坏的 tmux-pane 路径当作 durable-team runtime 成功证据。

**目标：** 在本机没有 `tmux` 且不在 `tmux` 会话内时，让用户级 OMX 仍能被所有本地项目以 native Windows 方式使用，同时不把 `native_omx` 错误定义为 `tmux`。

**架构：** Stage A 冻结契约并修正虚假完成口径。Stage B 用 TDD 区分 readiness 与 operational launchability，增加 Windows runtime-backend preflight，实现或 fail closed 到 Windows 原生 prompt/process controller，并证明跨项目 cwd 可用。

## 词汇

- `native_omx`：worker-centric durable backend family。
- `unix_tmux`：`native_omx` 家族内的 Unix/tmux runtime backend。
- `windows_prompt_process_controller`：`native_omx` 家族内的 Windows 原生 runtime backend。
- capability switches：`subagent_routing`、`oh_my_codex`、`langgraph`。
- backend family：`native_omx` 或 `langgraph`。
- effective lane：当前任务流按适配性选择的 lane。
- operational ability：当前是否真的能 launch、reuse、status、await、resume、shutdown。

## Stage A：冻结方案包

文件：

- 创建 `openspec/changes/fix-omx-windows-native-team-runtime-20260618/`，包含 proposal、design、tasks、management 与 delta spec。
- 创建本方案和中文 companion。
- 更新 `docs_bilingual/docs_registry.yaml`。
- 修正 `codex_oh_my_codex_user_level_team_mode_plan` 双语文件，使 P6 不再被误称为已完成运行能力。

步骤：

1. 冻结四层模型：能力开关、后端家族、effective lane、operational ability。
2. 冻结 runtime backend 词汇：`windows_prompt_process_controller`、`unix_tmux`、`unknown`。
3. 冻结 blocker token：`blocked:windows_backend_not_implemented`、`blocked:backend_not_ready`、`blocked:tmux_only_backend`、`blocked:not_in_tmux_session`、`blocked:controller_launch_failed`、`blocked:breakaway_process_unavailable`、`blocked:runtime_backend_unavailable`、`blocked:selector_refresh_gap`。
4. 运行 Stage A 验证：OpenSpec validate、document pair policy、precommit update/archive、OpenSpec guard。
5. 提交 Stage A 并通过 governance-confirmation local flow 合入本地 `main`。

## Stage B：Runtime 实现包

主要文件：

- `tools/install-codex-user-level-team-mode.ps1` - installer 与 generated wrapper source。
- `test/install-codex-user-level-team-mode.test.ps1` - generated wrapper 与 readiness regression tests。
- 如需更快 RED/GREEN，可新增聚焦 PowerShell 测试文件
- 只有触及 runtime patch replay 时才使用现有 `openclaw-omx-windows-*.mjs` 测试面

TDD 顺序：

1. RED：readiness false-ready。
2. RED：Windows backend selection。
3. RED：`omx-team-auto.ps1 -Apply` preflight fail-closed。
4. RED：live runtime evidence fields。
5. GREEN：增加 runtime 字段与 fail-closed preflight。
6. GREEN：实现 Windows prompt/process controller，或保留命名 blocker。
7. GREEN：接入 launch/reuse/switch/shutdown 与跨项目 cwd 验证。

## Stage B 验收

只有 fresh verification 证明以下内容后才接受：

- readiness 与 auto-helper 输出包含 `runtime_backend`、`preflight_passed`、`operational_ready`、`blockers`。
- `selected=true` 和 `ready=true` 不被当作 launch evidence。
- Windows 无 `tmux` 且不在 `tmux` 会话时不会走 tmux-only backend。
- `omx-team-auto.ps1 -Apply` 在 preflight 失败时先 fail closed，不写假状态。
- 如果声称 Windows run 成功，必须有 launch、status、await、resume、shutdown 生命周期证据。
- 用户级安装资产能从其他项目 cwd 使用，而 durable state 仍留在该项目自己的 `.omx/state/...`。

## 协同计划

- Stage A：leader 负责写文档和本地集成；专家只做 advisory，因为 frozen plan 尚未落地，且 durable-team runtime 正是 bug 对象。
- Stage B：Stage A 合入本地 `main` 后，按最小安全协同面切分 runtime readiness/lifecycle 与 test/docs。
- 如果现有 persistent team launcher 在修复前不能安全启动，记录命名 blocker，改用 native expert subagents 与主会话实现，不能把坏 team 当证据。

## 当前状态

<!-- CURRENT_STATUS_START -->
- Stage A 已经验证、提交并合入本地 `main`。
- Stage B 实现位于 worktree `implement-omx-windows-native-team-runtime-20260619`；聚焦 PowerShell 与 Node 验证已通过。
- Stage B 的 local gate、local MR review 与本地 `main` 集成仍待执行。
- 未授权远程发布。
<!-- CURRENT_STATUS_END -->

## 任务积压

<!-- TASK_BACKLOG_START -->
- Stage A：已完成 - OpenSpec delta、双语 implementation plan、docs registry 记录和 P6 runtime 口径修正已经冻结并集成。
- Stage B TDD：已完成 - PowerShell 测试覆盖 false-ready readiness、Windows backend selection、Apply preflight fail-closed 与 live runtime evidence fields。
- Stage B runtime：已完成 - 已实现 runtime backend/preflight 字段、Windows prompt/process controller 行为、生命周期 status/exit/shutdown replay patch 和跨项目 cwd 证据。
- Stage B 验证/集成：运行仓库治理检查，提交 runtime 包，运行 local gate/local MR review，合入本地 `main`，然后停在远程发布门。
<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- `openspec/changes/fix-omx-windows-native-team-runtime-20260618/` - Stage A OpenSpec 与 management 证据。
- `test/install-codex-user-level-team-mode.test.ps1` - Stage B wrapper/readiness 回归证据。
- `test/codex-official-update-patch-replay-template.test.ps1` - official-install replay gate、patch filtering、ordering 和 fail-closed 证据。
- `test/openclaw-omx-windows-prompt-*-fix.test.mjs` - Windows prompt controller lifecycle/startup/status/shutdown replay 证据。
- `tools/ci/ci_test_manifest.json` - 新增 Node 与 PowerShell 回归面的 CI 登记。
- `.omx/state/selectors/active.json` - 每个仓库的 selector authority。
- `.omx/state/team/codex-auto-managed-team.json` - 兼容 tracked native team record，本身不足以证明 launch。
<!-- EVIDENCE_INDEX_END -->
