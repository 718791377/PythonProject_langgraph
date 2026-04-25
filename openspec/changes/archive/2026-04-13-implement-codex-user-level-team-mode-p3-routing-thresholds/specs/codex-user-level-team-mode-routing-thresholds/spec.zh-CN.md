## ADDED Requirements

### Requirement: 安装器 SHALL 生成可检查的用户级 routing-policy 检查面

安装器 SHALL 在目标 Codex home 中生成 additive 的用户级 routing-policy 检查脚本。

生成资产集合 SHALL 包含：

- `bin/codex-routing-policy.ps1`

该检查输出 SHALL 为只读，并且 SHALL 反映与包装 `codex` 启动相同的 routing-policy 模型。

#### Scenario: 检查当前 routing policy

- **WHEN** 操作者执行 `codex-routing-policy.ps1 -Json`
- **THEN** 它 SHALL 输出当前启动模式、routing 模式以及角色路由可用性
- **AND** 它 SHALL 输出默认角色阈值、启动路径语义和仓库级运行态隔离说明

### Requirement: 包装启动 SHALL 从结构化 routing-policy 模型派生 developer instructions

生成的 shared support script SHALL 暴露一套结构化 routing-policy 模型，覆盖：

- 一般路由原则
- 各角色阈值
- 研究到实现交接规则
- 对抗式 bug 评审规则
- 包装 `codex` 与 `codex-native` 的启动路径语义

启动器 SHALL 从这套共享模型派生 developer-instruction 负载，而不是使用另一套无关的手写摘要。

#### Scenario: 自动路由注入批准的阈值规则

- **WHEN** 包装 `codex` 以 `oh_my_codex=off` 且 `subagent_routing=auto` 启动
- **THEN** 它 SHALL 注入包含批准专家角色阈值的 developer instructions
- **AND** 它 SHALL 将当前会话描述为“包装后的 native-routed 启动”，而不是“裸原生启动”

#### Scenario: manual routing 保留阈值规则但不主动自动路由

- **WHEN** 包装 `codex` 以 `subagent_routing=manual` 启动
- **THEN** 它 SHALL 在 developer instructions 中继续保留 routing policy 规则
- **AND** 它 SHALL 明确说明：除非用户显式要求，否则不做主动自动路由

#### Scenario: routing-off 模式关闭角色编排

- **WHEN** 包装 `codex` 以 `subagent_routing=off` 启动
- **THEN** 它 SHALL 关闭角色编排
- **AND** 它 SHALL 将当前会话描述为纯单代理排障路径

### Requirement: routing policy SHALL 保留批准的启动语义

routing policy SHALL 区分：

- 包装后的 native-routed 启动
- enhanced 启动
- pure-debugging 启动

它还 SHALL 保持这样一条规则：启用 oh-my-codex 会改变启动模式和能力开关，但不会在每次执行 `codex` 时自动拉起 durable team。

#### Scenario: enhanced 模式在操作者显式拉起团队前仍然只是启动模式

- **WHEN** 操作者全局启用 oh-my-codex 后再启动包装 `codex`
- **THEN** routing policy SHALL 报告 enhanced 启动
- **AND** 它 SHALL 不得声称 durable team 已被自动启动

### Requirement: 生成的 leader 与 playbook 资产 SHALL 镜像 routing 与隔离规则

生成的 `team-leader.toml` 与 `docs/team-mode-playbook.md` SHALL 记录：

- 包装 `codex` 与 `codex-native`
- 角色路由阈值
- 研究到实现交接纪律
- 对抗式 bug 评审用法
- 多项目运行态隔离依赖每仓库 `.omx` state root 的规则

#### Scenario: 用户在另一个仓库中阅读这些生成资产

- **WHEN** 用户在当前仓库之外打开生成的 leader profile 或 playbook
- **THEN** 这些资产 SHALL 仍然描述一套可跨仓库复用的工作模型
- **AND** 它们 SHALL 不依赖 OpenClaw 私有运行时命令
