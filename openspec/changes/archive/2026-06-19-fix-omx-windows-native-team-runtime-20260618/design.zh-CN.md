---
change_id: fix-omx-windows-native-team-runtime-20260618
lang: zh-CN
status: proposed
owner: codex
created_at: 2026-06-18
translation_of: openspec/changes/fix-omx-windows-native-team-runtime-20260618/design.md
---

# 设计：OMX Windows 原生团队运行时

## 四层模型

Stage A 固化四个互相独立的层：

1. 能力开关：`subagent_routing`、`oh_my_codex`、`langgraph` 表示哪些层启用。
2. 后端家族：`native_omx` 和 `langgraph` 是 durable backend family。
3. effective lane：当前任务流按适配性选择 worker-centric native OMX 或 graph-shaped LangGraph。
4. 运行能力：当前是否真的能 launch、reuse、inspect、await、resume、shutdown。

这些层不能互相代指；尤其 `selected=true` 或 `ready=true` 不能证明已经具备真实 launchability。

## 运行时后端契约

在 `native_omx` 家族内部，`runtime_backend` 表示具体实现：

- `windows_prompt_process_controller`：Windows 原生默认后端。
- `unix_tmux`：Unix/tmux 后端。
- `unknown`：无法证明具体运行时后端。

Windows 上如果没有显式请求 Unix/tmux，自动团队 helper 必须选择或 preflight Windows 原生后端，不能仅因缺少 `tmux` 就失败，也不能写出假 launch 记录。

## Preflight 与 blocker

运行态 preflight 必须报告：

- `runtime_backend` - concrete runtime implementation backend。
- `preflight_passed` - operational preflight 是否通过。
- `operational_ready` - 当前是否能执行 launch/reuse/status 生命周期动作。
- `blockers` - 稳定命名 blocker token。

稳定 blocker token 包括：

- `blocked:windows_backend_not_implemented` - Windows controller backend 尚未实现。
- `blocked:backend_not_ready` - selected durable backend 尚未 ready。
- `blocked:tmux_only_backend` - 当前只有 Unix/tmux runtime backend 可用。
- `blocked:not_in_tmux_session` - tmux-specific operation 不在 tmux session 内运行。
- `blocked:controller_launch_failed` - Windows controller launch attempt 失败。
- `blocked:breakaway_process_unavailable` - 所需 Windows breakaway process path 不可用。
- `blocked:runtime_backend_unavailable` - 当前没有可用 concrete runtime backend。
- `blocked:selector_refresh_gap` - selector state 需要 refresh 后才能 launch。

preflight 失败时，`omx-team-auto.ps1 -Apply` 必须返回结构化 blocked 结果，并且不能修改 tracked team state、active selector 或伪 launch receipt。

## 跨项目边界

用户级安装资产在 Codex home，例如 `C:\Users\lenovo\.codex`。每个仓库保留自己的 `.omx/state/...`。消费项目必须能从自己的 cwd 使用安装后的 OMX runtime，不能依赖 `D:\PythonProject_langgraph` 作为运行目录。
