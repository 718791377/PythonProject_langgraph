## ADDED Requirements（新增需求）

### Requirement: MCP Router log wrapper SHALL preserve protocol output while suppressing benign noise

仓库 SHALL 提供一个 opt-in wrapper（可选启用包装器），用于 MCP Router bridge execution（桥接执行），在保留 protocol-like stdout（类似协议的标准输出） 的同时，从 Codex 主会话中压制已知 benign non-protocol noise（无害非协议噪音）。

该 wrapper SHALL：

- 原样转发 JSON-RPC-like stdout（类似 JSON-RPC 的标准输出）。
- 从 stdout 与 stderr 中压制已知 benign non-protocol lines（无害非协议行）。
- 把每一行原始 stdout 与 stderr 写入带时间戳的本地日志文件。
- 把 actionable error lines（可操作错误行） 转发到 stderr。
- 把非零 child process exit code（子进程退出码） 报告到 stderr。

#### Scenario: Benign MCP Router lifecycle noise appears during a normal run

- **WHEN** 被包装的子命令输出 updater、workflow fallback、PNG 或 process-cleanup 这类无害噪音行
- **THEN** 这些行 SHALL 写入日志文件
- **AND** 它们 SHALL NOT 显示在主会话
- **AND** 正常 protocol-looking stdout SHALL 仍然被转发

#### Scenario: The child command emits an actionable error

- **WHEN** 被包装的子命令输出匹配 actionable error pattern（可操作错误模式） 的行
- **THEN** 该行 SHALL 写入日志文件
- **AND** 该行 SHALL 转发到 stderr

#### Scenario: The child command exits with a non-zero exit code

- **WHEN** 被包装的子命令以非零 exit code 退出
- **THEN** wrapper SHALL 返回相同 exit code
- **AND** 它 SHALL 向 stderr 写一行简短错误，并包含日志文件路径

### Requirement: MCP Router log wrapper SHALL NOT mutate user-level configuration

仓库实现 SHALL NOT 在新增 wrapper 时编辑 user-level Codex configuration（用户级 Codex 配置）、MCP Router database state（数据库状态） 或 token storage（令牌存储）。

#### Scenario: The wrapper is added to the repository

- **WHEN** 应用本仓库 change
- **THEN** `C:\Users\lenovo\.codex\config.toml` SHALL 不被仓库脚本修改
- **AND** MCP Router database state SHALL 不被仓库脚本修改
- **AND** operator documentation SHALL 把 wrapper 描述为 opt-in（可选启用）
