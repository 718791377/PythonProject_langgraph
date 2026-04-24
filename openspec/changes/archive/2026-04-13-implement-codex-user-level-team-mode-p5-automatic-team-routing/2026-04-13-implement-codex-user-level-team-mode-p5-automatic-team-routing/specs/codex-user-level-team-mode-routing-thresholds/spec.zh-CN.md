## MODIFIED Requirements

### Requirement: 安装器 SHALL 生成可检查的用户级 routing-policy surface

安装器 SHALL 在目标 Codex home 中生成 additive 的用户级 routing-policy inspection script。

生成的资产集 SHALL 包含：

- `bin/codex-routing-policy.ps1`

该 inspection 输出 SHALL 为只读，并且 SHALL 反映包装 `codex` 启动使用的同一套 routing-policy model。

该 inspection 输出还 SHALL 暴露：

- 生成的 burst-review role 集及其安装状态
- automatic durable-team routing section
- automatic durable-team routing 的 helper 路径
- tracked-team record 路径以及“不自动接管 unmanaged team”的规则

#### Scenario: P5 安装后检查 routing policy

- **WHEN** 操作员运行 `codex-routing-policy.ps1 -Json`
- **THEN** 它 SHALL 报告当前 startup mode、routing mode 和 role-routing availability
- **AND** 它 SHALL 暴露 durable-team phase map、helper 路径、reuse / switch / shutdown 规则和 tracked-team 安全边界

### Requirement: 包装启动 SHALL 从结构化 routing-policy model 派生 developer instructions

生成的 shared support script SHALL 暴露一套结构化 routing-policy model，覆盖：

- general routing principles
- role-specific thresholds
- research-to-implementation handoff rules
- adversarial bug-review rules
- wrapped `codex` 与 `codex-native` 的 startup-path semantics
- enhanced auto mode 下的 automatic durable-team routing semantics

startup launcher SHALL 从该 shared model 派生 developer-instruction payload，而不是使用无关的手写摘要。

#### Scenario: enhanced auto mode 暴露 durable-team helper 但不改变 startup 语义

- **WHEN** 包装 `codex` 在 `oh_my_codex=on` 且 `subagent_routing=auto` 下启动
- **THEN** 它 SHALL 注入提到 automatic durable-team helper 和 phase 阈值的 developer instructions
- **AND** 它 SHALL 明确说明 startup itself 仍不会自动拉起 durable team

### Requirement: 生成的 leader 与 playbook 资产 SHALL 镜像 routing 与 isolation 规则

生成的 `team-leader.toml` 与 `docs/team-mode-playbook.md` SHALL 记录：

- wrapped `codex` vs `codex-native`
- role-routing thresholds
- research-to-implementation handoff discipline
- adversarial bug-review usage
- automatic durable-team helper，以及何时应优先使用它而不是 raw `omx team`
- 多项目 runtime isolation 来自 per-repository `.omx` state roots 的规则

#### Scenario: 用户在 P5 安装后阅读生成资产

- **WHEN** 用户在本仓库外打开生成的 leader profile 或 playbook
- **THEN** 这些资产 SHALL 继续描述可复用的跨仓库 operating model
- **AND** 它们 SHALL 记录 durable-team helper、tracked-team 安全边界以及“不自动接管 unmanaged team”的规则
