## Why

当前用户级 team mode 已经具备：

- wrapped startup
- routing thresholds
- `team-leader.toml`
- durable-team helpers

但仍然缺少一层更强的启动期绑定，让每个新 wrapped Codex 会话都稳定表现为 leader-first routed session。

现在的新会话虽然能收到动态 `developer_instructions`，但并不总是会：

- 在第一次实质回答前完成任务分型
- 解释是否应调用 expert native subagents
- 解释是否已达到 `omx team` 阈值
- 输出可检查的 routing trace

因此下一批应正式收敛 startup leadership binding 与 first-turn routing 行为。

## What Changes

- 强化 wrapped startup，使每个新 wrapped Codex 会话都进入稳定的 leader-first routing posture
- 让启动期行为更明确地绑定到已安装的 `team-leader` 角色模型，而不是只把它当成一个旁置资产
- 让启动期输出简短的 first-turn routing trace
- 要求启动期说明这次为什么选择或没有选择 `omx team`
- 保持启动期分类与自动 durable-team launch 分离

- impact_scope:
  - wrapped `codex` startup path
  - user-level leader protocol binding
  - first-turn routing observability

- explicit_non_goals:
  - 不在每个新会话启动时自动拉起 durable team
  - 不改变原生 Codex bypass path
  - 不改变 `oh_my_codex` 与 `subagent_routing` 的全局控制语义

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-startup-leader-protocol`

### Modified Capabilities
- `codex-user-level-team-mode-startup-binding`
- `codex-user-level-team-mode-routing-thresholds`

## Impact

- affected_code:
  - user-level startup launcher
  - startup-bound developer instruction assembly
  - user-visible routing trace surface
- systems:
  - wrapped Codex session startup
  - leader-side routing explainability
