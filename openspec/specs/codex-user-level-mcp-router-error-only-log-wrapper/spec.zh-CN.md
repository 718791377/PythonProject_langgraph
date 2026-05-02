# codex-user-level-mcp-router-error-only-log-wrapper 规范

## Purpose / 目的

定义一个 opt-in repository-local wrapper，用于运行 MCP Router bridge command，同时只显示错误级诊断、保留 MCP protocol bytes，并保存完整 raw logs。`opt-in repository-local wrapper` 是需要操作者显式启用的仓库本地包装脚本；它不是默认全局配置。`MCP Router bridge command` 是 Codex 通过 MCP Router 调用共享 MCP server 时执行的桥接命令。

## Requirements / 需求

### Requirement: MCP Router log wrapper SHALL preserve protocol output while suppressing benign noise / MCP Router 日志包装器必须保留协议输出并抑制良性噪声

仓库必须提供一个 opt-in wrapper 用于 MCP Router bridge execution。`wrapper` 是 Codex 与 MCP Router 之间的本地包装层，用来保留协议字节、记录日志并降低 stderr 噪声。

wrapper 必须 byte-for-byte 保留 child stdout，因为 `stdout` 是 MCP protocol channel，用来承载 JSON-RPC 或 `Content-Length` framed protocol bytes。

wrapper 必须 byte-for-byte 将 wrapper stdin 复制到 child stdin，因为 `stdin` 承载 MCP protocol requests。

wrapper 必须过滤 visible child stderr：`stderr` 是诊断输出通道，actionable error line 继续转发到用户可见 stderr，benign stderr noise 只写入本地 log file。

wrapper 必须把 raw stdout 和 stderr chunks 写入 timestamped local log file。`timestamped local log file` 是带时间戳的本地日志文件，用于事后诊断。

wrapper 必须把 non-zero child process exit code 报告到 stderr，并返回相同 exit code。`non-zero exit code` 表示子进程失败。

#### Scenario: JSON-RPC stdout has no trailing newline / JSON-RPC stdout 没有末尾换行

- **WHEN** wrapped child command 输出没有 trailing newline 的 JSON-RPC stdout
- **THEN** wrapper 必须转发完全相同的 stdout bytes，不得追加 newline

#### Scenario: Content-Length framed stdout is emitted / 输出 Content-Length frame

- **WHEN** wrapped child command 输出 `Content-Length` framed stdout；这是 MCP stdio 常见的长度前缀协议帧
- **THEN** wrapper 必须转发完全相同的 stdout bytes，不得改写 header 或 body bytes

#### Scenario: Large tools/list stdout is emitted / 输出较大的 tools/list stdout

- **WHEN** wrapped child command 输出 large `tools/list`-like JSON-RPC response；`tools/list` 是 MCP 用来列出可用工具的协议方法
- **THEN** wrapper 必须完整转发 stdout payload，内容不得改变

#### Scenario: Benign MCP Router diagnostic noise appears on stderr / stderr 出现良性 MCP Router 诊断噪声

- **WHEN** wrapped child command 在 stderr 输出 updater、workflow fallback、PNG 或 process-cleanup 等良性噪声
- **THEN** 这些行必须写入 log file
- **AND** 这些行不得显示在 main session 中；`main session` 是当前 Codex 主会话输出界面

#### Scenario: The child command emits an actionable stderr error / 子命令输出可行动 stderr 错误

- **WHEN** wrapped child command 在 stderr 输出匹配 actionable error pattern 的行；`actionable error pattern` 是需要操作者看到并处理的错误模式
- **THEN** 该行必须写入 log file
- **AND** 该行必须转发到 stderr

#### Scenario: The child command exits with a non-zero exit code / 子命令以非零退出码退出

- **WHEN** wrapped child command 以 non-zero exit code 退出
- **THEN** wrapper 必须返回相同 exit code
- **AND** wrapper 必须向 stderr 写入一行简短错误信息，并包含 log file path；`log file path` 是完整诊断日志所在路径

### Requirement: MCP Router log wrapper SHALL NOT mutate user-level configuration / MCP Router 日志包装器不得修改用户级配置

仓库实现添加 wrapper 时，不得编辑 user-level Codex configuration、MCP Router database state 或 token storage。`user-level Codex configuration` 是用户级 Codex 配置；`MCP Router database state` 是 MCP Router 自己维护的服务配置状态；`token storage` 是 MCP Router 或相关工具保存凭据的位置。

`C:\Users\lenovo\.codex\config.toml` 是 user-level Codex configuration file；仓库脚本必须让它保持 operator-controlled。`operator-controlled` 表示只由操作者显式编辑或确认修改。

#### Scenario: The wrapper is added to the repository / 仓库新增 wrapper

- **WHEN** repository change 被应用
- **THEN** `C:\Users\lenovo\.codex\config.toml` 不得被仓库脚本修改
- **AND** MCP Router database state 不得被仓库脚本修改
- **AND** operator documentation 必须说明 wrapper 是 opt-in；`operator documentation` 是面向操作者的说明文档
