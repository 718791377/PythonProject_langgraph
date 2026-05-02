## Why（为什么）

MCP Router 当前会把无害的 lifecycle（生命周期） 与 updater（更新器） 噪音写进 Codex 会话，例如更新检查、workflow fallback（工作流回退） 消息、PNG profile 警告和 Windows 进程清理行。这些行不包含 secret，但会污染主会话上下文，并干扰后续冷启动会话判断。

## What Changes（改什么）

- 新增仓库本地 MCP Router log filter wrapper（日志过滤包装器），在保留正常 MCP protocol output（协议输出） 的同时，从主会话中压制已知无害的非协议噪音。
- 主会话只转发 actionable error output（可操作错误输出），同时把所有原始子进程输出写入带时间戳的日志文件。
- 增加测试，证明 protocol JSON 会保留、benign noise（无害噪音） 会被压制、错误会转发、非零退出会报告。
- 本 change 不修改 user-level Codex configuration（用户级 Codex 配置） 或 MCP Router database state（数据库状态）。

## Capabilities（能力）

### New Capabilities（新增能力）

- `codex-user-level-mcp-router-error-only-log-wrapper` - 提供安全、可选启用的 wrapper 模式，用来以“主会话只显示错误、完整日志本地保留”的方式运行 MCP Router bridge。

### Modified Capabilities（修改能力）

- 无。

## Impact（影响）

影响范围：

- `tools/mcp-router-log-filter-wrapper.ps1` - PowerShell launcher（启动器），为 Windows 操作员暴露 wrapper 入口。
- `tools/mcp_router_log_filter_wrapper.py` - Python filtering core（过滤核心），用来转发 stdio、保留协议输出并过滤可见日志。
- `test/mcp_router_log_filter_wrapper.test.ps1` - wrapper 行为的本地 PowerShell 测试文件。
- `openspec/changes/add-mcp-router-error-only-log-wrapper/` - 本功能的 OpenSpec change artifacts。

明确非目标：

- 不编辑 `C:\Users\lenovo\.codex\config.toml`；该文件是用户级 Codex 配置，必须由操作员控制。
- 不编辑 MCP Router database、token storage 或 UI state。
- 不隐藏 MCP JSON-RPC protocol messages（协议消息）。
- 不压制 actionable errors、authentication failures（认证失败）、exceptions（异常） 或非零进程退出。
- 不在当前 Codex 会话中自动启用该 wrapper。

发布顺序：

1. 增加 OpenSpec artifacts 与 wrapper 实现。
2. 增加测试，覆盖无害噪音、协议转发、错误转发和非零退出。
3. 运行本地验证。
4. 按 GitLab-first MR 流程发布。
5. 只有 review 后，操作员才可以手动决定是否把 Codex 的 `mcp_router` entry 指向 wrapper。

回滚方案：

- 回滚仓库提交，移除 wrapper 与测试。
- 因为本 change 不修改 user-level config，所以不需要 user-level runtime rollback。

验证路径：

- `powershell -NoProfile -ExecutionPolicy Bypass -File test/mcp_router_log_filter_wrapper.test.ps1` - 运行 wrapper 行为测试。
- `openspec validate --all` - 验证 OpenSpec artifacts。
- `python tools/run_openspec_guard.py --root . --json` - 运行仓库 guard checks。
- `git diff --check` - 检查补丁格式。

主线分类：

- 现有主线相邻维护：当前 Codex 用户级编排仓库中的 MCP Router scope 与 operator-surface hygiene（操作员表面卫生） 工作。
