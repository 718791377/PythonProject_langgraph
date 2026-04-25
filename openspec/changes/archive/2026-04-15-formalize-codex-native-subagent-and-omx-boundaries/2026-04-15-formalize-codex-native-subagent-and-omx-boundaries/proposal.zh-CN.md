## Why

用户级 Codex / oh-my-codex team mode 现在已经具备可工作的控制面、启动绑定、leader 路由以及原生 Windows durable-team 执行路径，但这些能力依赖的“原生 subagent 合同”在 spec 层还没有被正式化。这个缺口现在已经变成实际风险，因为双语实施方案文档已经补入了更严格的新规则，例如原生 Codex subagent 的定位、路由语义、agent TOML 放置边界、并发上限以及 OMX 分层；如果不把这些规则提升到 OpenSpec requirement，后续 wrapper、生成器、文档和实现就可能继续漂移。

## What Changes

- 新增一个正式 capability，用于定义用户级 team mode 工作流里的原生 Codex subagent 边界。
- 把原生 Codex subagent 明确定义为“官方原生能力，显式触发，受限 fan-out，leader 侧 fan-in”，而不是模拟 pane 体系，也不是默认无限制自动运行时。
- 扩展生成出来的用户级控制面，使其覆盖通用用户级 agent TOML、仓库级 agent TOML、独立 custom agent 的最小 schema，以及 `agents.max_threads` / `agents.max_depth` 的显式查看或管理能力。
- 明确自动专家角色路由是 leader 侧路由策略，建立在原生 Codex subagent 之上，而不是把裸 Codex 描述成默认会自动拉起专家角色。
- 增加执行安全规则：默认优先读多写少 fan-out；写多型并行只有在 ownership 隔离、热点串行规则和 leader 最终集成都已定义时才允许。
- 统一 leader profile、playbook 和 operator 指南中的分层表述，明确区分“原生 Codex subagent”“durable `omx team`”和“通用可编程多 agent 编排运行时”。
- 保留已经批准的启动语义：`oh_my_codex=off` 且 routing 开启时仍然是 wrapped native-routed 启动；`oh_my_codex=off` 且 routing 关闭时才是纯单代理路径。

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-native-subagent-boundaries`：正式定义用户级 team mode 工作流中的原生 Codex subagent 语义、custom agent 配置边界、并发上限、写隔离规则以及 OMX 术语边界

### Modified Capabilities
- `codex-user-level-team-mode-controls`：扩展生成控制资产，使其覆盖原生 subagent 上限控制面，以及用户级 / 仓库级 agent TOML 放置规则
- `codex-user-level-team-mode-routing-thresholds`：明确自动角色路由是 leader 侧策略，建立在原生 Codex subagent 的显式触发之上，并增加 bounded fan-out 与写并行安全约束

## Impact

- impact_scope:
  - 用户级 Codex team-mode 控制资产
  - wrapped 启动与 routing-policy 合同
  - 生成出来的 leader / playbook / operator 指南
  - Codex / oh-my-codex 用户级 team mode 相关的 OpenSpec capability 定义
- explicit_non_goals:
  - 不替换原生 `codex`、`codex.cmd`、`codex.ps1`
  - 不新增 durable-team backend 或 worker lifecycle 实现
  - 不把 mixed-pane compose 层变成默认形态
  - 不引入 WSL2 路径
  - 不修改 OpenClaw runtime 配置
- rollout_sequence:
  - 先定义 proposal、design 与 spec delta，正式化 native-subagent 合同
  - 再扩展 controls 与 routing-policy requirement
  - 后续实现阶段再落地生成资产与验证覆盖
  - 实现稳定后再同步 plan、playbook 与 operator-facing 文档
- rollback_plan:
  - 只回滚实现阶段新增或修改的增量控制资产、routing-policy 表面与生成文档
  - 始终保持原生 Codex base layer 不变
  - 如果受管 limit 写入行为不稳定，则退回到只读 inspection 模式，同时保留边界合同
- validation_path:
  - 运行 `openspec validate --all`
  - 验证 installer 可以把资产生成到 repo-local Codex home 目标路径
  - 验证 wrapped native-routed 启动与 plain single-agent 启动的语义区分
  - 验证控制面可以查看或管理 `agents.max_threads` 与 `agents.max_depth`
  - 验证生成指南能区分用户级 `~/.codex/agents` 与仓库级 `.codex/agents`
  - 验证写多型并行规则必须依赖显式 ownership 隔离与 leader 集成
- mainline_classification:
  - 属于 existing mainline continuation
  - 更具体地说，这是 Codex 用户级 team-mode 控制面与路由面上的 contract-tightening change
