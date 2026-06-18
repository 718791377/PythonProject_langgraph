---
change_id: fix-omx-windows-native-team-runtime-20260618
lang: zh-CN
status: proposed
owner: codex
created_at: 2026-06-18
translation_of: openspec/changes/fix-omx-windows-native-team-runtime-20260618/proposal.md
---

# 提案：修复 OMX Windows 原生团队运行时

## 背景

用户级自动协同会在 worker-centric 场景选择 `native_omx`。本机问题很明确：当前没有 `tmux`，也不在 `tmux` 会话内，因此如果实际实现仍只会走 Unix/tmux pane，就不能启动真实持久团队。

本变更先冻结语义：`native_omx` 是 worker-centric durable backend family，不是 `tmux` 的同义词。`tmux` 只是 Unix 实现后端；Windows 默认需要原生 prompt/process controller 后端和运行态证据。

## 变更内容

- 固化四层模型：能力开关、后端家族、任务流 effective lane、运行能力。
- 固化 readiness/selected 不能等同于 launchability。
- Windows `native_omx` 默认走原生进程控制后端，除非显式请求 Unix/tmux 后端。
- helper 输出必须包含 `runtime_backend`、`preflight_passed`、`operational_ready` 和稳定 blocker token。
- `omx-team-auto.ps1 -Apply` 在 preflight 失败时必须 fail closed，不能写入假团队状态。
- 用户级资产属于 Codex home；每个项目自己的 `.omx/state/...` 仍是 durable truth。

## 不在范围

- 把 WSL2 或 Unix `tmux` 作为 Windows 默认要求。
- 把 wrapper、plan 或 selector 当成真实团队已启动证据。
- 把消费项目 durable state 移入本仓库。
- 任何远程发布。
