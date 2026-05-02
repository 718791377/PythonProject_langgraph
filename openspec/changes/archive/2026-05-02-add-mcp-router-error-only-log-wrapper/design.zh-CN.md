## Overview（概览）

该 wrapper 是一个可选启用的仓库本地 process wrapper（进程包装器），用于 MCP Router bridge command。它的目标是减少会话污染，同时不修改用户级配置，也不丢失诊断证据。

## Design（设计）

`tools/mcp-router-log-filter-wrapper.ps1` 是一个很薄的 PowerShell launcher（启动器）。它会调用 `tools/mcp_router_log_filter_wrapper.py`，后者是 Python filtering core（过滤核心），负责启动子命令、捕获 stdout 与 stderr，并按行分类：

- Protocol-like stdout（类似协议的标准输出） 会原样转发到 stdout。Protocol-like line 指 JSON object（JSON 对象） 中带 JSON-RPC 字段、`Content-Length` 或 `Content-Type` header，或空的 framing line（帧分隔行）。
- 已知 benign non-protocol noise（无害非协议噪音） 只写入带时间戳的日志文件。
- 未知 non-protocol informational output（非协议信息输出） 也只写入日志文件。
- Actionable error output（可操作错误输出） 会写入日志文件并转发到 stderr。
- 子进程非零 exit code（退出码） 会转发到 stderr，并附带日志路径。

默认 benign filters（无害过滤规则） 包括：

- `checking-for-update` - MCP Router updater check noise（更新检查噪音）。
- `update-not-available` - MCP Router updater result noise（更新结果噪音）。
- `No valid workflows found for` - MCP Router workflow fallback noise（工作流回退噪音）。
- `Executing handler directly without workflow` - MCP Router fallback execution noise（回退执行噪音）。
- `libpng warning: iCCP` - Electron 或 PNG color-profile warning noise（色彩配置警告噪音）。
- `SUCCESS: The process with PID ... has been terminated.` - 生命周期管理产生的 Windows process-tree cleanup noise（进程树清理噪音）。

默认 error filters（错误过滤规则） 包括：

- `ERROR` - 通用高严重度标记，通常表示子命令遇到失败。
- `FAILED` - 通用失败标记，通常表示某个操作没有成功完成。
- `Exception` - runtime exception（运行时异常） 标记，通常表示程序抛出了意外错误。
- `Traceback` - Python stack trace（堆栈跟踪） 标记，通常表示异常逃逸了正常处理。
- `Unauthorized` - authentication failure（认证失败） 标记，通常表示凭据或权限被拒绝。
- `Forbidden` - authorization failure（授权失败） 标记，通常表示调用方缺少权限。
- `auth failed` - 一些命令行工具使用的小写认证失败短语。
- `token expired` - token lifetime failure（令牌过期） 短语，通常表示凭据需要刷新或轮换。

## Safety Boundaries（安全边界）

- wrapper 是 opt-in（可选启用），本 change 不把它写入 `C:\Users\lenovo\.codex\config.toml`。
- wrapper 永远不压制看起来像 JSON-RPC 的 stdout，因为该流可能承载 MCP protocol messages（协议消息）。
- wrapper 会把全部原始子进程输出记录到本地日志文件，便于后续诊断。
- wrapper 不编辑 MCP Router database 或 token storage。

## Validation（验证）

PowerShell 测试会创建短生命周期 fake child commands（伪子命令） 并验证：

- benign stdout/stderr lines 不出现在 wrapper 可见输出中
- JSON-RPC stdout 被保留
- error stderr 被转发
- 非零 exit status 被传播并报告
- raw logs 保留被压制的 benign lines
