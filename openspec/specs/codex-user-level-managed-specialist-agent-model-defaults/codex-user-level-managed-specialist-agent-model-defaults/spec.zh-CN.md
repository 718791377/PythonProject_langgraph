# codex-user-level-managed-specialist-agent-model-defaults 规范

## 目的

定义用户级 Codex 专家 agent profile 的可复现安装器托管模型默认值和陈旧模型清理规则。适用范围包括 native experts、durable teams 与 persistent-team helpers。

## Requirements

### Requirement: 用户级安装器必须让托管专家 profiles 使用受支持的 GPT-5.4 或 GPT-5.5 模型

用户级安装器必须在用户级 agents 目录下生成托管的 `team-leader.toml`、`verifier.toml`、`debugger.toml`、`researcher.toml`、`dependency-expert.toml`、`writer.toml`、`bug-finder.toml`、`bug-rebutter.toml` 和 `bug-judge.toml` 专家 profiles。

所有安装器托管的专家 profiles 必须声明且只声明一个来自受支持 allowlist 的顶层 `model` 值：`gpt-5.4` 或 `gpt-5.5`。

安装器不得在托管的用户级 agent TOML 中生成 `gpt-5.3*`、`gpt-5.3-codex*`、`gpt-5.4-mini` 或 `gpt-5.5-mini`。

#### Scenario: 操作员安装托管的用户级专家 profiles

- **WHEN** 安装器把托管的用户级资产渲染到目标 Codex home
- **THEN** 它必须在该位置生成托管专家 TOML
- **AND** 每个生成的 TOML 必须只使用 `model = "gpt-5.4"` 或 `model = "gpt-5.5"`
- **AND** 这些文件必须作为托管资产参与 backup、rollback 和后续 refresh

### Requirement: 执行关键 specialists 必须使用 GPT-5.5，支持/研究 specialists 必须使用 GPT-5.4

托管的 `team-leader`、`verifier` 和 `debugger` profiles 必须使用 `gpt-5.5`。

托管的 `researcher`、`dependency-expert`、`writer`、`bug-finder`、`bug-rebutter` 和 `bug-judge` profiles 必须使用 `gpt-5.4`。

#### Scenario: 操作员检查生成的专家 profiles

- **WHEN** 操作员读取生成的托管专家 profiles
- **THEN** `team-leader.toml`、`verifier.toml` 和 `debugger.toml` 必须各自声明 `model = "gpt-5.5"`
- **AND** `researcher.toml`、`dependency-expert.toml`、`writer.toml`、`bug-finder.toml`、`bug-rebutter.toml` 和 `bug-judge.toml` 必须各自声明 `model = "gpt-5.4"`

### Requirement: 安装器必须把现有用户级 agent TOML 中的陈旧模型标识归一化掉

用户级安装器必须在写入托管资产后扫描现有用户级 `agents/*.toml`，并把任何不在受支持 allowlist 内的顶层 `model` 值归一化为符合角色职责的受支持模型。

当嵌入式元数据引用（例如 `resolved_model:`）或精确模型指导文本包含陈旧模型标识时，安装器也必须归一化这些引用。

#### Scenario: 操作员刷新包含陈旧用户级 agents 的 Codex home

- **GIVEN** 目标 Codex home 包含带有 `gpt-5.3-codex*` 或 `gpt-5.4-mini` 的现有 agent TOML
- **WHEN** 安装器成功完成
- **THEN** 这些 TOML 不得再包含 `gpt-5.3*`、`gpt-5.3-codex*`、`gpt-5.4-mini` 或 `gpt-5.5-mini`
- **AND** install manifest 必须包含一个 `agent_model_policy` section，用来报告 allowed models 和 normalized files
