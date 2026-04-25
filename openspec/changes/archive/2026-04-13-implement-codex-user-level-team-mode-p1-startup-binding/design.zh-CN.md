## Context

`P0` 已经提供了：

- 增量式用户级控制资产
- 独立持久化的 `oh_my_codex` 与 `subagent_routing` 状态
- 安装前备份快照与失败自动回滚
- 不触碰原生 `codex` 入口的验证路径

现在缺的是把这些状态真正桥接到普通 `codex` 启动上的运行时绑定层。

当前真实用户环境说明：

- 原生 Codex 实际解析到 npm 安装的 `C:\Users\lenovo\AppData\Roaming\npm\codex.cmd`
- 当前 PowerShell profile 很轻，没有包装 `codex`
- `codex-cli 0.120.0` 支持通过 `-c key=value` 与 `--disable <feature>` 做运行时覆盖
- 当前 `~/.codex/config.toml` 已经带有 oh-my-codex 倾向的配置

因此，最安全、最可回退的绑定面就是：在 PowerShell profile 中加入一个托管 block，包装 `codex`，但完全不改原生可执行文件。

## Goals / Non-Goals

**Goals:**

- 把普通 PowerShell `codex` 启动接到持久化的 team-mode 状态上
- 保持 npm 安装的原生 `codex` 文件完全不变
- 提供一个显式 `codex-native` 旁路入口，随时绕过包装层
- 在 `oh_my_codex=off` 时关闭 omx 相关启动行为
- 在 `subagent_routing=off` 时关闭 multi-agent 启动路由
- 把备份与回滚覆盖扩展到 PowerShell profile 路径

**Non-Goals:**

- 本阶段不绑定 `cmd.exe` 启动
- 不替换 npm 安装的 `codex` 命令
- 不修改 OpenClaw runtime 设置
- 不在这里实现 mixed-pane 编排

## Decisions

### Decision 1：用托管的 PowerShell profile block，而不是替换原生可执行文件

启动绑定将通过向用户 PowerShell profile 注入托管 block 来实现。

这个 block 会定义：

- `codex`
  - 一个很薄的函数，转发到生成的 launcher 脚本
- `codex-native`
  - 一个很薄的函数，直接转发到原生 npm 安装的 Codex 命令

原因：

- PowerShell 函数优先级允许拦截 `codex`，但不需要修改 npm 安装文件
- 这种绑定方式保持增量、可回退
- `codex-native` 提供即时逃生入口

### Decision 2：launcher 负责把状态翻译成 Codex CLI 覆盖参数

生成的 launcher 脚本会读取 `state/user-level-team-mode.json`，并把状态映射成运行时参数。

核心映射：

- `oh_my_codex=on`
  - 使用 team-mode developer instructions
  - 保持 omx MCP servers 启用
- `oh_my_codex=off`
  - 使用 native-mode developer instructions
  - 禁用 omx MCP servers
  - 禁用 omx notify hook
- `subagent_routing=auto`
  - 保持 multi-agent 可用
  - 使用自动路由说明
- `subagent_routing=manual`
  - 保持 multi-agent 可用
  - 使用手动路由说明
- `subagent_routing=off`
  - 通过 `--disable multi_agent` 禁用 multi-agent
  - 使用无路由说明

原因：

- `codex-cli 0.120.0` 已经支持 `-c` 与 `--disable`
- 运行时覆盖能避免破坏性修改原生 Codex 安装
- 这种“状态到参数”的映射可以用 fake native Codex 做测试

### Decision 3：生成由 launcher 自己管理的 developer-instruction 预设

launcher 不再依赖 `config.toml` 顶层已有的 `developer_instructions`。

它会自己生成并管理这些小型预设：

- omx-enabled auto routing
- omx-enabled manual routing
- native auto routing
- native manual routing
- no-routing / pure debugging

原因：

- 包装层需要与 team-mode 状态严格一致的确定性行为
- 如果依赖现有 config 文本，不同机器上的启动行为会发生漂移
- 自己持有预设文本，跨项目行为才稳定

代价：

- 通过包装层启动的 PowerShell `codex` 会话，将由 launcher 管理，而不是直接服从原始 config 文本
- 通过 `codex-native` 旁路入口来缓解这个代价

### Decision 4：备份与回滚必须把外部 profile 路径当作一等目标

`P0` 的备份逻辑已经覆盖了 Codex home 内部文件。

`P1` 要把同一事务扩展到：

- 生成的 launcher 脚本
- Codex home 外部的 PowerShell profile 文件

原因：

- profile 是新的关键修改面
- profile 只要写坏，影响会比缺少一个 helper script 更大
- 用户已经明确要求出错后及时恢复

### Decision 5：本阶段只支持 PowerShell 启动绑定

安装器本阶段只绑定基于 PowerShell 的 `codex` 启动。

它不会尝试改动：

- `cmd.exe`
- npm 安装的 `codex.cmd`
- npm 安装的 `codex.ps1`

原因：

- PowerShell 是当前面向用户的 shell，也是方案里标准化的 Windows 路径
- 这样可以把绑定面保持得足够窄、足够可回退
- 避免跨 shell 模糊行为与 PATH 级破坏

## Risks / Trade-offs

- [Risk] 被包装的 PowerShell 启动行为可能与原始 `codex.cmd` 有差异。
  Mitigation: 提供 `codex-native`，并保持原生可执行文件完全不变。

- [Risk] launcher 自己管理的 developer instructions 可能与未来 Codex 或 oh-my-codex 预期漂移。
  Mitigation: 保持预设文本尽量窄，只围绕路由模式展开。

- [Risk] 从 `cmd.exe` 启动时不会获得启动绑定。
  Mitigation: 明确把 PowerShell 作为本阶段支持的 shell。

- [Risk] 编辑 profile 会引入更高风险的修改面。
  Mitigation: 扩展时间戳备份快照与回滚逻辑，把 profile 也纳入事务保护。

## Migration Plan

1. 创建 `P1` 的 proposal、design、spec、tasks 工件。
2. 扩展安装器，加入 launcher 生成与托管 profile block 注入。
3. 增加 fake native Codex 测试路径，验证运行时参数映射。
4. 验证 profile 回滚与 `codex-native` 旁路行为。
5. 运行 OpenSpec 校验与仓库 guard 校验。
6. 只有仓库级验证通过后，才重新安装到真实用户 home。
