## Why / 为什么

当前 MCP Router wrapper 会按行分类 stdout。`MCP Router wrapper` 是 Codex 调用 MCP Router 时使用的本地包装脚本，用来记录日志并过滤噪声。MCP stdio transport 可以输出 JSON-RPC 行、`Content-Length` frame、很大的 `tools/list` payload，或者不带换行的写入。`stdout` 是 MCP 协议通道，用来传输客户端和服务端之间的协议字节；如果 wrapper 在行边界重写 stdout，可能破坏协议 framing，并可能导致 Codex 启动或 `/resume` 这个恢复历史会话的命令不稳定。

## What Changes / 变更内容

- 将 wrapper stdout 改为 byte-transparent：`stdout` 是 MCP 协议输出通道，child process 输出的每个字节都原样转发到 wrapper stdout。
- 继续把完整 raw stdout/stderr 写入本地日志：`raw stdout/stderr` 是未经过滤的子进程输出，用于事后诊断。
- 只过滤 visible stderr：`stderr` 是错误和诊断输出通道，良性噪声只写日志，actionable error 继续显示给操作者。
- 增加测试覆盖 JSON-RPC no trailing newline、`Content-Length` framed output、large `tools/list`-like payload、benign stderr suppression 和 non-zero exit propagation：这些测试用于证明 wrapper 不破坏 MCP 协议字节。
- 保持 wrapper opt-in：`wrapper opt-in` 表示该包装器仍需显式启用，本 change 不会重新启用 Codex user-level `mcp_router`。

## Non-goals / 非目标

- 不修改 `C:\Users\lenovo\.codex\config.toml`：这是用户级 Codex 配置文件。
- 不修改 MCP Router database 或 token storage：这些是 MCP Router 自己维护的连接和凭据状态。
- 不移除当前 resume-stability exception：这是为了保持 `/resume` 可见性而保留的临时禁用例外。
- 不宣称 wrapper 已适合作为 Codex 默认启动配置，直到 operator testing 证明 `/resume` 仍能正常显示历史会话。
