## MODIFIED Requirements / 修改后的需求

### Requirement: MCP Router log wrapper SHALL preserve protocol output while suppressing benign noise / MCP Router 日志包装器必须保留协议输出并抑制良性噪声

wrapper 必须 byte-for-byte 保留 child stdout，因为 `stdout` 是 MCP 协议通道，用来承载 JSON-RPC 或 `Content-Length` framed protocol bytes。

wrapper 必须过滤 visible child stderr：`stderr` 是诊断输出通道，actionable error line 继续转发到用户可见 stderr，benign stderr noise 只写入本地 log file。

#### Scenario: JSON-RPC stdout has no trailing newline / JSON-RPC stdout 没有末尾换行

- **WHEN** wrapped child command 输出没有 trailing newline 的 JSON-RPC stdout
- **THEN** wrapper 必须转发完全相同的 stdout bytes，不得追加 newline

#### Scenario: Content-Length framed stdout is emitted / 输出 Content-Length frame

- **WHEN** wrapped child command 输出 `Content-Length` framed stdout；这是 MCP stdio 常见的长度前缀协议帧
- **THEN** wrapper 必须转发完全相同的 stdout bytes，不得改写 header 或 body bytes

#### Scenario: Large tools/list stdout is emitted / 输出较大的 tools/list stdout

- **WHEN** wrapped child command 输出 large `tools/list`-like JSON-RPC response；`tools/list` 是 MCP 用来列出可用工具的协议方法
- **THEN** wrapper 必须完整转发 stdout payload，内容不得改变
