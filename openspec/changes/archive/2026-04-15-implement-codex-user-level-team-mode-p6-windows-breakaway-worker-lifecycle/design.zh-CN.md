## Context

已归档的 `P6` 批次已经证明：

- 原生 Windows durable team 可以启动
- runtime-root isolation 可以把 worker sidefiles 隔离出 worker worktree

后续 live 验证暴露出的剩余问题更聚焦：

- backend 本身已经不再被 `tmux` 阻塞
- 剩余失败点是父 shell 退出后的 Windows worker 存活与生命周期跟踪
- 普通 detached child 启动在原生 Windows 下不是足够强的持久边界
- 当 worker 真正活下来后，shutdown 也必须能针对真实 controller pid 干净收口

## Goals / Non-Goals

**Goals**

- 给 Windows prompt workers 提供更强的 breakaway launcher 路径
- 记录并跟踪真实长寿命 controller pid
- 让 live worker liveness 与 shutdown 行为对齐新的启动路径
- 让 Windows prompt worker 指南明确 controller-owned ACK / initial claim 行为

**Non-Goals**

- 不重写 leader-side routing
- 不改 Unix backend
- 不增加新的 durable-team phase

## Decisions

### Decision 1: 这是生命周期修正批次，不是新的路由批次

Why:

- 路由阈值和 tracked-team planning 已经存在
- 真实失败发生在 launch decision 之后

### Decision 2: 用比普通 detached child 更强的 Windows launcher 路径

Why:

- 普通 detached child 在原生 Windows 下仍然可能跟着父 shell 生命周期一起消失
- launcher 跳板可以把真实 controller pid 回传给 runtime

### Decision 3: 即使中间 launcher 立即退出，也要跟踪真实 controller pid

Why:

- liveness checks 与 shutdown 应该跟踪实际拥有 worker loop 的进程
- 短寿命 launcher pid 不是可靠的 durable lifecycle identity

### Decision 4: worker startup guidance 必须和 controller-managed startup 保持一致

Why:

- 一旦 controller 已经代发 startup ACK 和 first claim，worker prompt 就不该再盲目重试
- Windows constrained PowerShell 下，重复 inline `--input` JSON 会制造大量噪声

## Risks / Trade-offs

- [Risk] 更强的 launcher 路径可能让 shutdown 变复杂。
  Mitigation: 保持 pid tracking 显式，并用真实 live team 验证 clean shutdown。

- [Risk] 指南变化可能和 Unix worker 行为产生偏差。
  Mitigation: 把新规则限定在 native Windows Codex prompt workers。

## Validation Plan

1. 启动一个新的 Windows durable team，验证 launching shell 退出后 workers 仍然存活。
2. 验证 task claims 保持在 `in_progress`，而不会立刻转成 `worker_stopped`。
3. 对 live team 执行一次干净的 `omx team shutdown ... --force --confirm-issues`。
4. 验证跨仓库 tracked-team isolation 仍然成立。
