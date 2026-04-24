## ADDED Requirements

### Requirement: 安装器必须生成用户级 burst-review agent profiles

安装器必须把增量式用户级 agent profiles 生成到目标 Codex home 中。

生成资产至少必须包括：

- `agents/bug-finder.toml`
- `agents/bug-rebutter.toml`
- `agents/bug-judge.toml`

除非显式强制，否则安装器不得覆盖这些路径上的 unmanaged 文件。

#### Scenario: 在临时 Codex home 中生成 burst-review agent profiles

- **WHEN** 安装器针对显式指定的目标 Codex home 运行
- **THEN** 它必须在那里生成三个 burst-review 角色配置
- **AND** 它必须保持这些新文件为 additive-only

### Requirement: 生成出来的 burst-review 角色必须保持 leader 侧、默认只读

生成出来的 `bug-finder`、`bug-rebutter`、`bug-judge` profiles 必须被定义为 leader 侧的短突发审查角色。

它们必须默认采用只读审查行为，且不得把自己表述为持久 worker pane。

#### Scenario: 操作者检查生成出来的角色定义

- **WHEN** 用户打开生成出来的 burst-review agent 文件
- **THEN** 每个 profile 都必须说明自己是 leader 侧 burst-review 角色
- **AND** 每个 profile 都必须保持默认只读的审查纪律

### Requirement: 生成出来的 burst-review 角色必须编码对抗式审查契约

生成出来的角色 prompt 必须编码批准后的对抗式审查闭环：

- `bug-finder` 以带权严重度评分方式最大化可疑 bug 召回
- `bug-rebutter` 在非对称计分压力下尽量证伪弱 bug claim
- `bug-judge` 负责仲裁两边报告，并只保留需要继续升级处理的幸存项

#### Scenario: 检查用户级安装中的 burst-review 行为定义

- **WHEN** 安装后检查生成出来的角色文件
- **THEN** 三份 prompt 必须分别暴露 finder、rebutter、judge 的不同职责
- **AND** 只有 judge 才能决定哪些问题可以升级到执行或调试 lane

### Requirement: burst-review agent 生成必须纳入备份快照与失败回滚

安装器必须把 burst-review agent 文件纳入与其他用户级团队模式资产相同的备份快照与失败回滚事务。

#### Scenario: 部分安装失败时恢复 burst-review 的安装前状态

- **WHEN** 在 burst-review agent 文件已经写入后安装失败
- **THEN** 安装器必须恢复之前已存在的 managed burst-review 文件
- **AND** 对于 fresh install，必须移除新建的 burst-review 文件
- **AND** 必须保留备份元数据供诊断使用
