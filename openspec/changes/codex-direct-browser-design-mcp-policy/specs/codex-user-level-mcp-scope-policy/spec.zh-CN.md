## MODIFIED Requirements / 修改后的需求

### Requirement: Browser and design MCP servers SHALL remain direct Codex utility servers / 浏览器和设计 MCP server 必须保持 Codex 直连

Codex 必须通过 Codex 直连 MCP entry 使用浏览器和设计 MCP 能力，而不是通过 Codex 侧 `mcp_router` bridge。

Codex 直连通用 MCP server 包括 `chrome-devtools` 和 `pencil`。

#### Scenario: Codex browser and design tools are configured / 配置 Codex 浏览器和设计工具

- **WHEN** 审计本地 Codex 配置
- **THEN** `chrome-devtools` 和 `pencil` 必须作为 Codex 直连 MCP server 启用
- **AND** Codex 不得要求 MCP Router 才能访问这些能力

### Requirement: Codex SHALL keep the MCP Router bridge disabled by default / Codex 必须默认禁用 MCP Router bridge

Codex 侧 `mcp_router` bridge 默认必须禁用或不存在。

#### Scenario: Codex MCP Router bridge is enabled / Codex MCP Router bridge 被启用

- **WHEN** Codex `mcp_router` bridge 已启用
- **THEN** checker 必须失败
- **AND** 操作者必须被引导使用 Codex 直连 MCP entry
