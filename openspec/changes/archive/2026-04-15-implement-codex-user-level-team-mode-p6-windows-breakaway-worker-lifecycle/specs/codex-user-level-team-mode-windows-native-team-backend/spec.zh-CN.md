## MODIFIED Requirements

### Requirement: `omx team` SHALL 支持原生 Windows durable-team backend

durable-team runtime SHALL 支持一个不依赖 WSL2 或 Unix `tmux` 的原生 Windows backend。

#### Scenario: 原生 Windows prompt workers 在父 shell 退出后继续存活

- **WHEN** 原生 Windows durable team 通过 Windows backend 启动 prompt-mode Codex workers
- **THEN** 这些 workers SHALL 在 launching shell 退出后继续运行
- **AND** backend SHALL 不依赖那种会随着父 shell 一起退出的普通 detached child

### Requirement: 原生 Windows backend SHALL 保持 repo-local team state contract

原生 Windows backend SHALL 保持 `.omx/state/team/...` 下相同的 repo-local state 布局。

至少 SHALL 保持：

- team manifest 与 config
- task files
- mailbox state
- worker identity
- worker heartbeat

#### Scenario: controller-managed startup 不再把重复 ACK / claim 循环泄漏进 Windows worker 执行

- **WHEN** Windows backend controller 已经为 prompt worker 发送了 startup ACK 和 initial task claim
- **THEN** worker guidance SHALL 不再要求盲目重试同一批 startup 动作
- **AND** Windows worker prompts SHALL 优先采用基于当前 state 的继续执行，而不是重复 startup 控制流

### Requirement: 原生 Windows backend SHALL 支持生命周期对齐

原生 Windows backend SHALL 支持：

- `status`
- `await`
- `resume`
- `shutdown`

#### Scenario: 对 breakaway-launched Windows team 执行干净 shutdown

- **WHEN** 操作员针对通过 breakaway launcher 路径启动的原生 Windows team 运行 `omx team shutdown <team-name>`
- **THEN** runtime SHALL 干净停止真实 controller-owned worker processes
- **AND** 它 SHALL 不依赖短寿命 launcher pid 来保证 shutdown 正确性
