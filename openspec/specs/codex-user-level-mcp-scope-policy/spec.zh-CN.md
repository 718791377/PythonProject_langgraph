# codex-user-level-mcp-scope-policy 规范

## Purpose / 目的

定义用户级 MCP server 边界：哪些 MCP server 由 Codex 直连使用，哪些 MCP Router server 只供非 Codex 客户端使用。

## Requirements / 需求

### Requirement: Codex-private MCP servers SHALL remain direct Codex servers / Codex 私有 MCP server 必须保持 Codex 直连

Codex 私有 MCP server 必须直接配置给 Codex，不能作为共享 server entry 通过 MCP Router 管理。

Codex 私有 MCP server 包括 `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace`。

#### Scenario: Codex starts with oh-my-codex enabled / Codex 启动且启用 oh-my-codex

- **WHEN** Codex 启动且 oh-my-codex 层已启用
- **THEN** `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` 必须作为 Codex 直连 MCP server 可用
- **AND** 这些 server 不得要求通过 MCP Router

#### Scenario: MCP Router is audited / 审计 MCP Router

- **WHEN** 审计 MCP Router managed server records
- **THEN** `omx_state`、`omx_memory`、`omx_code_intel` 或 `omx_trace` 的 active records 必须报告为 drift
- **AND** 操作者必须被引导将这些 server 保持为 Codex 私有

### Requirement: Browser and design MCP servers SHALL remain direct Codex utility servers / 浏览器和设计 MCP server 必须保持 Codex 直连

Codex 必须通过 Codex 直连 MCP entry 使用浏览器和设计 MCP 能力，而不是通过 Codex 侧 `mcp_router` bridge。

Codex 直连通用 MCP server 包括 `chrome-devtools` 和 `pencil`。

`chrome-devtools` 是浏览器调试 MCP server，用于浏览器页面、DOM 快照、截图、控制台数据和网络检查。

`pencil` 是设计 MCP server，用于 Pencil 设计文档、视觉变量、节点读取和导出。

#### Scenario: Codex browser and design tools are configured / 配置 Codex 浏览器和设计工具

- **WHEN** 审计本地 Codex 配置
- **THEN** `chrome-devtools` 和 `pencil` 必须作为 Codex 直连 MCP server 启用
- **AND** Codex 不得要求 MCP Router 才能访问这些能力

#### Scenario: MCP Router also serves non-Codex clients / MCP Router 同时服务非 Codex 客户端

- **WHEN** MCP Router 为 Trae、VS Code、PyCharm 或其他非 Codex 客户端包含 `chrome-devtools` 或 `pencil`
- **THEN** 该 Router 状态不算作 Codex 访问路径
- **AND** Codex 必须继续使用对应的 Codex 直连 MCP entry

### Requirement: Codex SHALL keep the MCP Router bridge disabled by default / Codex 必须默认禁用 MCP Router bridge

Codex 侧 `mcp_router` bridge 默认必须禁用或不存在。

Codex 正常启动时不得加载 MCP Router 的全量工具目录。

重新启用 Codex 侧 `mcp_router` bridge 必须经过未来另一个已批准的治理变更；该变更必须定义有边界的 Codex 专用 Router profile，并验证 `tools/list` 大小、resume 启动和直连 MCP fallback 行为。

#### Scenario: Codex configuration is audited / 审计 Codex 配置

- **WHEN** Codex `mcp_router` bridge 已禁用或不存在
- **THEN** checker 必须通过该 bridge 状态
- **AND** checker 不得要求为禁用 bridge 声明临时 exception

#### Scenario: Codex MCP Router bridge is enabled / Codex MCP Router bridge 被启用

- **WHEN** Codex `mcp_router` bridge 已启用
- **THEN** checker 必须失败
- **AND** 操作者必须被引导使用 Codex 直连 MCP entry

### Requirement: MCP Router SHALL NOT manage itself / MCP Router 不得管理自身

MCP Router 不能包含 `mcp-router`、`mcp_router` 或其他 Router 自引用 managed server entry。

#### Scenario: Router self-reference is detected / 检测到 Router 自引用

- **WHEN** MCP Router managed server records 包含 `mcp-router` 或 `mcp_router`
- **THEN** checker 必须报告 self-reference drift
- **AND** 操作者必须删除或禁用该自引用 Router server entry

### Requirement: MCP scope policy SHALL have script-backed validation / MCP 范围策略必须有脚本校验

MCP 范围策略必须由可执行 checker 支撑，该 checker 能验证本地 Codex 配置并报告 MCP Router drift。

#### Scenario: Repository guard runs without user-level runtime files / 仓库 guard 在没有用户级 runtime 文件的环境中运行

- **WHEN** 仓库 guard 在 CI 或其他没有用户级 Codex 或 MCP Router 文件的环境中运行
- **THEN** checker 必须用 informational output 跳过本地 runtime validation
- **AND** guard 必须继续验证仓库拥有的 policy artifacts

#### Scenario: Strict local audit is requested / 请求 strict 本地审计

- **WHEN** 操作者使用 strict Router-state validation 运行 checker
- **THEN** Codex 私有 server 的 active MCP Router records 必须成为 blocking errors
- **AND** active Router self-reference records 必须成为 blocking errors

#### Scenario: Codex direct MCP server is disabled / Codex 直连 MCP server 被禁用

- **WHEN** 本地 Codex 配置中缺失或禁用了 `omx_state`、`omx_memory`、`omx_code_intel`、`omx_trace`、`chrome-devtools` 或 `pencil`
- **THEN** checker 必须失败

### Requirement: Legacy Resume MCP Workarounds SHALL Be Scoped Per Invocation / 旧会话 Resume 的 MCP 绕过必须限定为单次启动

当某个陈旧旧 thread 无法干净启动时，旧会话必须把临时 per-invocation MCP override（单次启动 MCP 覆盖）限定在受影响的旧 thread 范围内。

per-invocation MCP override 是一次性的 Codex 配置覆盖，例如 `-c "mcp_servers.omx_code_intel.enabled=false"`。

此类覆盖不得被当成永久禁用 Codex 私有 MCP server 或默认编辑用户级 Codex 配置的授权。

#### Scenario: A legacy old thread fails on one direct MCP server / 某个旧 thread 因一个直连 MCP server 失败

- **GIVEN** 旧会话因为陈旧的 direct MCP startup state 失败
- **WHEN** 操作者继续该旧 thread
- **THEN** 可以仅对该次启动使用 per-invocation override 禁用受影响 server
- **AND** 新会话的 direct MCP policy 必须保持不变

#### Scenario: A new wrapped session starts normally / 新 wrapped session 正常启动

- **GIVEN** oh-my-codex 已为正常工作启用
- **WHEN** 新 wrapped session 启动
- **THEN** `omx_state`、`omx_memory`、`omx_code_intel`、`omx_trace`、`chrome-devtools` 和 `pencil` 必须继续受 direct Codex MCP policy 约束
- **AND** 旧会话 workaround 不得全局移除这些 server
