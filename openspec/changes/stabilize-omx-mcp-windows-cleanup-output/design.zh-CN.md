## 背景

操作者希望保留 `codex-ohmy` 流程：先打开一个临时 Codex 会话，然后在 TUI 内输入 `/resume`。`codex-ohmy` 是用户级包装入口；`/resume` 是 Codex TUI 内部恢复旧会话的命令。

禁用 `omx_*` MCP server 可以证明噪声来源，但这不是可接受的长期修复，因为这些 server 是 `subagent / omx / langgraph` 编排基线的一部分。

因此修复点应放在 Windows cleanup-output 边界。wrapper 必须保留完整 `omx_*` 能力，把任何 shim 限定在 wrapped launch 内，并避免全局修改 `config.toml`。

## 决策

### 添加 scoped Windows cleanup shim 目录

安装器将在用户级 Codex bin 目录下生成 `win-shims` 目录。`win-shims` 是生成目录，包含仅供 wrapped Codex launch 使用的 Windows 命令 shim。

该目录包含：

- `taskkill.cmd`：CMD shim，调用真实 `taskkill.exe` 并抑制成功输出。
- `taskkill.ps1`：PowerShell shim，提供同样的成功输出抑制合同。
- `taskkill-shim-source.cs`：可选 `taskkill.exe` shim 的 C# 源码，用于本机存在 C# 编译器时生成 executable shim。
- 可选 `taskkill.exe`：编译后的 executable shim，用于捕获显式调用 `taskkill.exe` 而不是 `taskkill` 的调用方。

### 将 shim 限定在 `codex-ohmy` 子进程树

生成的 startup launcher 会在调用 native Codex 命令前，把 `win-shims` 放到 `$env:Path` 前面，并在调用结束后恢复原始 PATH。`$env:Path` 是当前进程及子进程查找命令的路径变量。

这样 shim 会对 native Codex 子进程树可见，包括临时会话内 `/resume` 触发的 cleanup，但不会改变操作者的全局 shell 状态。

### 保留错误和证据

shim 会调用真实 `%SystemRoot%\System32\taskkill.exe`。如果退出码为 0，它抑制 stdout 和 stderr。若退出码非 0，它把捕获的输出转发到 stderr，并返回相同退出码。

第一版实现保持可见通道干净且确定。如果后续证据表明操作者需要完整 cleanup 日志，可以在 follow-up 中添加有界日志路径，而不改变成功输出抑制合同。

### 保持 `omx_*` MCP direct 和 enabled

当 `oh_my_codex=on` 时，launcher 继续传入 `mcp_servers.omx_state.enabled=true`、`mcp_servers.omx_memory.enabled=true`、`mcp_servers.omx_code_intel.enabled=true` 和 `mcp_servers.omx_trace.enabled=true`。这些 `-c` 参数是 Codex 启动时的配置覆盖。

## 已考虑的替代方案

- 禁用 `omx_*` MCP server：拒绝，因为这会移除长期编排能力。
- 要求 `codex-ohmy resume <session-id>`：拒绝，因为操作者明确希望先进入临时会话再 `/resume`。
- 使用 MCP Router 承载 `omx_*`：拒绝，因为 Codex-private `omx_*` MCP server 属于 direct Codex config。
- 管道过滤整个 Codex TUI 输出：拒绝，因为这可能破坏交互式终端行为。

## 风险和缓解

- 显式调用 `taskkill.exe` 的调用方可能绕过仅 CMD 的 shim。缓解：生成 C# 源码，并在本机存在编译器时可选生成 `taskkill.exe`。
- PATH 作用域可能误影响父 shell。缓解：用 `try/finally` 包裹 native Codex 调用，并恢复原始 PATH 和 PATHEXT。
- shim 可能隐藏真实失败。缓解：非零退出保留原始退出码，并把捕获输出转发到 stderr。

## 验证

- 安装器测试确认 shim 文件已生成。
- 安装器测试确认 wrapped launch 会把 `win-shims` 放到 PATH 前面，并继续转发用户参数。
- checker 测试确认安装器在 `oh_my_codex=on` 时仍启用 `omx_*` MCP，并且存在 cleanup-output control layer。
- OpenSpec validation 确认需求合同有效。
