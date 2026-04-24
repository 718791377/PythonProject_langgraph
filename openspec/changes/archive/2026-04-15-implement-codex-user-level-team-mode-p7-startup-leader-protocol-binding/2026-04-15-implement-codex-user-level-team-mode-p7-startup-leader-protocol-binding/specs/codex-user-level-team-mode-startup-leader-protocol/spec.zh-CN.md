## ADDED Requirements

### Requirement: 每个 wrapped Codex 会话 SHALL 以 leader-first routing posture 启动

当 startup 通过用户级 wrapped `codex` 入口路由时，新会话 SHALL 以稳定的 leader-first routing posture 开始，而不是只带着路由能力却表现成普通会话。

#### Scenario: 在 enhanced auto mode 下启动一个新的 wrapped Codex 会话

- **WHEN** 操作员以 `oh_my_codex=on` 且 `subagent_routing=auto` 启动一个新的 wrapped Codex 会话
- **THEN** 会话 SHALL 将自己识别为 leader-first routed session
- **AND** 它 SHALL 在第一次实质回答前把当前主 Codex CLI 会话视为 leader lane

### Requirement: wrapped startup SHALL 在第一次实质回答前完成 task-shape classification

wrapped startup SHALL 在第一次实质回答前执行首轮 task-shape check。

至少 SHALL 判定：

- 当前任务是否仍处于早期分析或规划阶段
- 当前是否需要 leader-side expert native subagents
- 当前是否已经满足 durable-team threshold

#### Scenario: startup 看到的是一个前期任务

- **WHEN** 初始任务仍然不清晰，或仍处于 planning 阶段
- **THEN** startup SHALL 将其分类为尚未达到 durable-team-ready
- **AND** 它 SHALL 不应表现得像 `omx team` 已经被选中一样

### Requirement: wrapped startup SHALL 输出可检查的 first-turn routing trace

wrapped startup SHALL 暴露一段简短 routing trace，用于解释首轮路由决策。

这段 trace 至少 SHALL 能解释：

- 哪个 expert role set 被选中或被跳过
- `omx team` 阈值是满足还是未满足
- 为什么当前会话保持 bursty，或为什么升级到 durable team 使用

#### Scenario: startup 没有选择 `omx team`

- **WHEN** 初始任务尚未满足 durable-team threshold
- **THEN** 首轮 routing trace SHALL 解释是哪条 threshold 没有满足
- **AND** 它 SHALL 不应让操作者去猜测这是路由失败还是被有意延后
