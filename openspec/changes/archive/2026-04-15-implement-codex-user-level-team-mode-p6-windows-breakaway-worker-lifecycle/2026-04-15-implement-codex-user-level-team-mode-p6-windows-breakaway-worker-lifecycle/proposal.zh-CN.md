## Why

已归档的 `P6` 已经建立了原生 Windows durable-team backend，但后续 live 验证又暴露出两类应单独追踪的 Windows 修正点，不能再悄悄塞回已归档批次：

- 以普通 detached child 方式拉起的 worker controller，仍可能随着父 shell 退出而死亡
- Windows prompt worker 的提示仍会诱导重复 startup ACK / claim，以及在受限 PowerShell 下使用脆弱的 `--input` JSON 形式

因此需要一个独立的 `P6` 后续修正批次，正式收敛 breakaway worker launch、pid 精确跟踪，以及 Windows 下 controller-owned startup 行为。

## What Changes

- 加固原生 Windows prompt worker 启动路径，使 durable workers 在父 shell 退出后继续存活
- 让 worker pid 跟踪反映真实长寿命 controller 进程，而不是短寿命 launcher 跳板
- 让 `status / await / shutdown` 语义与新的 launcher 形态保持一致
- 通过更新 worker 指南，减少 Windows 下重复 ACK / initial claim 与脆弱 `--input` JSON 模式
- 保持 repo-local team state isolation 与 runtime-root isolation 不变

- impact_scope:
  - 原生 Windows durable-team runtime
  - worker lifecycle tracking
  - worker bootstrap guidance

- explicit_non_goals:
  - 不引入 WSL2 路径
  - 不修改 Unix `tmux` 路径
  - 不改变原生 Codex 保护策略
  - 不引入 mixed persistent pane compose layer

- rollout_sequence:
  1. 先正式定义这一批修正的范围与验收面
  2. 为 Windows prompt workers 实现 breakaway launcher 路径
  3. 让 shutdown 与 liveness tracking 对齐新的 controller pid
  4. 更新 Windows worker guidance，说明 controller 可能已代发 ACK / initial claim
  5. 重新执行原生 Windows live 验证

## Capabilities

### Modified Capabilities
- `codex-user-level-team-mode-windows-native-team-backend`

## Impact

- affected_code:
  - oh-my-codex team runtime
  - Windows worker controller launch path
  - worker bootstrap guidance
- systems:
  - 原生 Windows durable team lifecycle
  - repo-local team state 与 tracked-team 操作面
