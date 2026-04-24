## ADDED Requirements

### Requirement: 仓库必须提供一个仓库内安装器，用于生成用户级团队模式控制资产

仓库必须提供一个安装器或生成器，能够把用户级 Codex 团队模式控制资产生成到显式指定的 Codex home 目标路径，而不是在仓库开发阶段直接写入真实用户 home。

生成资产集合至少必须包含：

- `agents/team-leader.toml`
- `bin/_codex-user-level-team-mode.ps1`
- `bin/codex-omx-on.ps1`
- `bin/codex-omx-off.ps1`
- `bin/codex-omx-status.ps1`
- `bin/codex-subagents-auto.ps1`
- `bin/codex-subagents-manual.ps1`
- `bin/codex-subagents-off.ps1`
- `bin/codex-routing-status.ps1`
- `state/user-level-team-mode.json`

#### Scenario: 把 P0 控制层生成到一个临时 Codex home

- **WHEN** 使用显式目标 Codex home 路径运行安装器
- **THEN** 它必须在目标路径下创建所需的增量式资产
- **AND** 生成逻辑必须能够在同一用户配置文件下复用于任意项目仓库

### Requirement: 安装器必须保留原生 Codex 基础层

安装器不得创建、替换或修改这些原生基础入口名称：

- `codex`
- `codex.cmd`
- `codex.ps1`

即使重复生成用户级团队模式资产，这条安全边界也必须成立。

#### Scenario: 目标 home 中已经存在原生 Codex 哨兵文件

- **WHEN** 安装器面向一个已经包含 `codex.cmd` 或 `codex.ps1` 的 Codex home 运行
- **THEN** 这些文件必须保持不变
- **AND** 安装器仍然只能生成增量式团队模式资产

### Requirement: 生成出的控制面必须把 `oh_my_codex` 与 `subagent_routing` 分别持久化

生成出的控制面必须在一个共享状态文件中分别持久化 `oh_my_codex` 与 `subagent_routing`。

生成控制脚本至少必须支持这些取值：

- `oh_my_codex`: `on`, `off`
- `subagent_routing`: `auto`, `manual`, `off`

默认生成状态必须是：

- `oh_my_codex = off`
- `subagent_routing = auto`

#### Scenario: 初次安装创建默认原生路由状态

- **WHEN** 安装器创建新的状态文件
- **THEN** 状态必须默认 `oh_my_codex=off`
- **AND** 必须默认 `subagent_routing=auto`

#### Scenario: 操作者切换 oh-my-codex 而不改变路由状态

- **WHEN** 操作者运行 `codex-omx-on.ps1` 或 `codex-omx-off.ps1`
- **THEN** 只有 `oh_my_codex` 字段可以变化
- **AND** `subagent_routing` 必须保持不变

#### Scenario: 操作者切换路由状态而不改变 oh-my-codex

- **WHEN** 操作者运行 `codex-subagents-auto.ps1`、`codex-subagents-manual.ps1` 或 `codex-subagents-off.ps1`
- **THEN** 只有 `subagent_routing` 字段可以变化
- **AND** `oh_my_codex` 必须保持不变

#### Scenario: 纯净排障模式由两套开关共同推导

- **WHEN** 持久化状态变成 `oh_my_codex=off` 与 `subagent_routing=off`
- **THEN** 生成的状态输出必须报告 pure debugging mode
- **AND** 必须报告 role orchestration 不可用

### Requirement: 生成的 leader profile 必须表示“当前主 Codex CLI 会话”

生成的 `team-leader.toml` 必须把“当前主 Codex CLI 会话”描述为 leader lane。

它不得把 leader 重新定义成一个单独的常驻 worker pane。

#### Scenario: 维护者读取生成的 leader profile

- **WHEN** 读取生成的 `team-leader.toml`
- **THEN** 它必须把当前主 Codex CLI 会话描述为 team leader
- **AND** 必须继续把 worker 语义与 leader 语义分开

### Requirement: 安装器默认必须拒绝覆盖非托管冲突文件

如果某个目标生成路径已经存在文件，但该文件没有被标记为托管团队模式资产，安装器必须失败，而不是静默覆盖。

#### Scenario: 用户已经在某个 wrapper 路径上有自己的文件

- **WHEN** 安装器在 `bin/codex-omx-on.ps1` 这类目标生成路径上遇到一个非托管文件
- **THEN** 安装器默认必须报错停止
- **AND** 不得静默覆盖该冲突文件

### Requirement: 安装器必须创建备份快照并回滚部分失败

在安装器写入任何生成资产或创建状态文件之前，它必须先在目标 Codex home 内的 namespaced backup root 下创建一个带时间戳的备份快照，用于覆盖所有目标托管路径。

如果安装器在开始写入后失败，它必须自动恢复所有目标路径的安装前状态，并保留备份快照元数据供检查。

#### Scenario: 失败的重装会恢复之前的托管资产内容

- **WHEN** 安装器已经开始更新托管 team-mode 资产，随后遇到运行期失败
- **THEN** 它必须把所有目标托管路径恢复到安装前的内容或安装前不存在的状态
- **AND** 它必须保留可供排障或后续人工恢复使用的备份元数据
- **AND** 原生 `codex` 命名文件必须保持不变

#### Scenario: 失败的首次安装会移除新建的托管文件

- **WHEN** 安装器面对一个此前没有 team-mode 资产的目标 Codex home，并且在写入开始后失败
- **THEN** 它必须在回滚期间删除这次失败安装中新建的托管资产文件
- **AND** 它必须保留记录本次安装尝试的备份快照 manifest
