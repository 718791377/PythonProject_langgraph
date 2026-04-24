## Context

P5 已经完成了 leader-side 路由层：

- 包装启动在 enhanced auto mode 下能暴露 durable-team capability
- `omx-team-auto.ps1` 已经能规划 `launch`、`reuse`、`switch`、`shutdown`
- tracked repo-local team metadata 也已经存在

现在真正缺的，是 native Windows 下能执行这些动作的 runtime backend。

当前真实故障形态是：

- planning 可以正常工作
- `-Apply` 已经到达 runtime 边界
- runtime 因为 `omx team` 仍然要求 `tmux` 而失败

## Goals / Non-Goals

**Goals:**

- 给 `omx team` 增加 backend abstraction
- 保留现有 Unix `tmux` backend
- 增加一个不依赖 WSL2 的 native Windows durable-team backend
- 保持 `.omx/state/team/...` 合同在不同 backend 间稳定
- 让 `omx-team-auto.ps1 -Apply` 在 native Windows 下真正可执行

**Non-Goals:**

- 不重写 P0-P5 的路由或控制模型
- 不把 WSL2 变成标准路径
- 不替换 native Codex 启动
- 不把 GUI pane 自动化作为第一版稳定 backend

## Decisions

### Decision 1：把 routing 与 execution backend 分开

P5 已经解决了“怎么路由”的问题。P6 要解决的是“怎么执行 backend”的问题。

Why:

- 路由层已经可检查且有测试
- 当前阻塞点在其下层

### Decision 2：在 `omx team` 下增加 backend abstraction

`omx team` 应在运行时解析 backend：

- Unix 路径：继续使用现有 `tmux`
- Windows 路径：新增 native backend

Why:

- 平台相关的 worker 启动方式本来就属于 backend 问题
- backend 之上的 status 与 state 语义应该保持一致

### Decision 3：优先做 Windows process backend，而不是 pane-oriented backend

第一版 Windows backend 应把 durable workers 作为受控后台进程启动，并继续使用 repo-local state 与 dedicated worktree。

Why:

- 进程编排比 GUI pane 自动化更稳
- 生命周期控制更容易做成可测试的东西
- P5 需要的是 durable execution，而不是视觉上的 pane 效果

### Decision 4：保持 state、mailbox、worktree 合同不变

不同 backend 间都保持：

- `.omx/state/team/<team>/...`
- mailbox 与 task files
- worker identity 与 heartbeat
- worker worktree ownership
- `status / await / resume / shutdown / api` 语义

Why:

- 这样可以保护现有用户级 wrapper surface
- 也能避免破坏 P2 到 P5

## Risks / Trade-offs

- [Risk] Windows process cleanup 可能比 tmux cleanup 更难。
  Mitigation：把 worker identity、pid tracking、shutdown ack、stale-worker detection 显式化。

- [Risk] backend 分化可能让平台行为漂移。
  Mitigation：在 backend 之上保持统一的 state contract 和 lifecycle contract。

- [Risk] 现有 wrapper 文档可能再次和 runtime 现实漂移。
  Mitigation：backend 能力变化时同步更新 playbook 与 policy。

## Migration Plan

1. 创建 P6 的 proposal、design、tasks 和 spec delta。
2. 给 `omx team` 增加 backend abstraction。
3. 实现 native Windows backend。
4. 验证 wrapper 兼容性与 `omx-team-auto.ps1 -Apply`。
5. 只有 native Windows runtime 测试通过后才继续向前推进。
