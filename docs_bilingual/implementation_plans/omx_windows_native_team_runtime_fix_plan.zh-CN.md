---
doc_id: omx_windows_native_team_runtime_fix_plan
lang: zh-CN
doc_class: implementation_plan
status: final
translation_of: docs_bilingual/implementation_plans/omx_windows_native_team_runtime_fix_plan.md
change: fix-omx-windows-native-team-runtime-20260618
base_ref: 2d53bd73c8a8b9202d6643fe26985960c7a740a0
archived-with: 2026-06-19-fix-omx-windows-native-team-runtime-20260618
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
- Stage B runtime 实现已经验证、提交并在 `5cd3491` 合入本地 `main`，且已通过受保护 local flow 清理。
- 2026-06-19 已从当前仓库源码刷新用户级 managed helpers，`codex-ohmy doctor --summary --no-color --ascii` 报告 `0 fail`。
- 从 `D:\project` 执行的跨项目 live smoke 已证明 Windows 原生 prompt/process backend 可在无 tmux 时 launch、status、await、处理无 stale handle 的 resume、shutdown 与 cleanup。
- 未授权且未执行远程发布。
<!-- CURRENT_STATUS_END -->

## 任务积压

<!-- TASK_BACKLOG_START -->
- Stage A：已完成 - OpenSpec delta、双语 implementation plan、docs registry 记录和 P6 runtime 口径修正已经冻结并集成。
- Stage B TDD：已完成 - PowerShell 测试覆盖 false-ready readiness、Windows backend selection、Apply preflight fail-closed 与 live runtime evidence fields。
- Stage B runtime：已完成 - 已实现 runtime backend/preflight 字段、Windows prompt/process controller 行为、生命周期 status/exit/shutdown replay patch 和跨项目 cwd 证据。
- Stage B 验证/集成：已完成 - 聚焦测试、仓库 gate、local MR review、受保护本地 main 集成、安装刷新和跨项目 live smoke 证据均已完成；当前停在远程发布门。
<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- `openspec/changes/archive/2026-06-19-fix-omx-windows-native-team-runtime-20260618/` - Stage A OpenSpec 与 management 证据；archive promotion 前记录 archive/sync 证据。
- `test/install-codex-user-level-team-mode.test.ps1` - Stage B wrapper/readiness 回归证据。
- `test/codex-official-update-patch-replay-template.test.ps1` - official-install replay gate、patch filtering、ordering 和 fail-closed 证据。
- `test/openclaw-omx-windows-prompt-*-fix.test.mjs` - Windows prompt controller lifecycle/startup/status/shutdown replay 证据。
- `tools/ci/ci_test_manifest.json` - 新增 Node 与 PowerShell 回归面的 CI 登记。
- `C:\Users\lenovo\.codex\bin\omx-team-auto.ps1`、`codex-durable-state-status.ps1`、`_codex-user-level-team-mode-launcher.ps1` - 所有本地项目共用的已刷新用户级 managed helper artifacts。
- `D:\project\.omx\state\prompt-controller-debug\windows-native-prompt-process\worker-1.controller.log` - 跨项目 smoke 的真实 launch/controller 证据。
- `D:\project\.omx\reports\team-commit-hygiene\windows-native-prompt-process.md` 与 `.context.json` - 跨项目 smoke 的 shutdown/finalization 证据。
- `.omx/state/selectors/active.json` - 每个仓库自己的 selector authority；不能替代真实 launch evidence。
- `.omx/state/team/codex-auto-managed-team.json` - 兼容 tracked native team record（如存在），本身不足以证明 launch。
<!-- EVIDENCE_INDEX_END -->

## Live Runtime 证据 - 2026-06-19

Stage B 本地 main 集成后的 fresh machine evidence：

- Windows 目标上下文：`TMUX=<unset>`，`tmux=<not found>`。
- 用户级安装刷新：`powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\install-codex-user-level-team-mode.ps1 -Force` 已重写 `C:\Users\lenovo\.codex\bin` 下的 managed helpers；`omx-team-auto.ps1`、`codex-durable-state-status.ps1`、`_codex-user-level-team-mode-launcher.ps1` 时间戳为 2026-06-19T08:56:57Z-08:56:59Z。
- wrapped entry 健康检查：`codex-ohmy doctor --summary --no-color --ascii` 结束为 `15 ok | 1 idle | 5 notes | 2 warn | 0 fail degraded`。
- 已安装 CLI 表面：`omx --version` 输出 `oh-my-codex v0.12.5`；`omx team --help` 包含 `native Windows defaults to the prompt/process worker backend; Unix keeps the tmux backend.`。
- readiness projection：`omx-team-auto.ps1 -Task "windows native prompt process completion evidence" -Phase execute-parallel -ParallelSlices 2 -RepoRoot D:\PythonProject_langgraph -Json` 输出 `runtime_backend`、`preflight_passed`、`operational_ready`、`blockers`；native OMX readiness 条目报告 `runtime_backend=windows_prompt_process_controller`、`preflight_passed=true`、`operational_ready=true`，并正确区分用户级 LangGraph selection 与 native OMX launch evidence。
- 跨项目 live smoke 从 `D:\project` 执行：`omx team 1:team-executor "windows native prompt/process live smoke 20260619 1700: say SMOKE_READY briefly then wait for shutdown"` 创建 team `windows-native-prompt-process`，状态位于 `D:\project\.omx\state\team` 与 `D:\project\.omx\state\prompt-controller-debug`。
- launch 证据：`config.json` / `manifest.v2.json` 记录 `worker_launch_mode: "prompt"`、`tmux_session: "prompt-windows-native-prompt-process"`、`leader_pane_id: null`、`hud_pane_id: null`、worker `pid: 20456`、child pid `30816`、`team_state_root: "D:\project\.omx\state"`。
- controller 证据：`worker-1.controller.log` 记录 `controller_start`、`startup_ack`、`claim_task`、`launch_exec`，且 `launchMode: "codex_exec_direct_js"`。
- status 证据：`omx team status windows-native-prompt-process --json` 返回 `status: "ok"`、`phase: "team-exec"`、workers total/dead/non-reporting 为 `1/0/0`，且有一个 in-progress task。
- await/resume 证据：`omx team await ... --timeout-ms 10000 --json` 在初始 ACK 之后无新事件而 timeout，不是 launch 失败；`omx team resume ...` 报告无 resumable handle，紧随其后的 status 仍为 `ok`。
- shutdown 证据：`omx team shutdown windows-native-prompt-process --force --confirm-issues` 以 `merge_outcome: noop`、`Team shutdown complete` 完成，生成 `D:\project\.omx\reports\team-commit-hygiene` 报告，post-status 返回 `status: "missing"`。
- cleanup/isolation 证据：pid `20456` 与 `30816` 均已不存在，`D:\project` 保持 `main` clean，没有 `windows-native-prompt-process` worktree registration，`D:\PythonProject_langgraph` 没有 smoke team state/worktree；路径校验后已删除 `D:\project\.omx\team\windows-native-prompt-process` 空残留目录。
- 远程边界：未授权、未执行 GitLab/GitHub 远程发布。
