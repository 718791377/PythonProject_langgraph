## MODIFIED Requirements

### Requirement: 安装器必须生成可检查的用户级 routing-policy 检查面

安装器必须把增量式用户级 routing-policy 检查脚本生成到目标 Codex home 中。

生成资产集必须包括：

- `bin/codex-routing-policy.ps1`

检查输出必须是只读的，并且必须反映 wrapped `codex` 启动时使用的同一份 routing-policy 模型。

检查输出还必须暴露生成出来的 burst-review 角色集合，以及每个 burst-review 角色当前是否已作为可调用的用户级资产安装。

#### Scenario: 在 burst-review 角色安装后检查当前 routing policy

- **WHEN** 操作者运行 `codex-routing-policy.ps1 -Json`
- **THEN** 它必须报告当前启动模式、路由模式以及角色编排可用性
- **AND** 它必须暴露默认角色阈值、启动路径语义以及仓库级 runtime 隔离说明
- **AND** 当对应用户级 profile 已存在时，它必须把 `bug-finder`、`bug-rebutter`、`bug-judge` 显示为已安装的可调用角色

### Requirement: 生成出来的 leader 与 playbook 资产必须镜像路由和隔离规则

生成出来的 `team-leader.toml` 与 `docs/team-mode-playbook.md` 必须记录：

- wrapped `codex` 与 `codex-native`
- 角色路由阈值
- 先研究后实现的交接纪律
- 对抗式 bug-review 的使用方式
- 多项目 runtime 隔离来自每仓库 `.omx` state roots 的规则

当 burst-review 角色已生成时，这些资产必须把它们描述为真实存在的 leader 侧可调用角色，而不是抽象的未来占位说明。

#### Scenario: 用户在其他仓库中阅读 P4 安装后的生成资产

- **WHEN** 用户在本仓库之外打开生成出来的 leader profile 或 playbook
- **THEN** 这些资产仍必须描述一个可跨仓库复用的操作模型
- **AND** 它们不得依赖 OpenClaw 特有的 runtime 命令
- **AND** 它们必须把 burst-review triad 描述为已生成、可调用的用户级角色
