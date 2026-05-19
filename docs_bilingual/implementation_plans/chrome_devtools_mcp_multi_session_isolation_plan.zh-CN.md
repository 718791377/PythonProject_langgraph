---
doc_id: chrome_devtools_mcp_multi_session_isolation_plan
lang: zh-CN
doc_class: implementation_plan
status: draft
---

# Chrome DevTools MCP 多项目多会话隔离与清理方案

## 1. 背景

多个项目、多个 Codex session 同时使用 `chrome-devtools-mcp` 时，不能共用同一个 Chrome `userDataDir`。
默认目录通常是：

```text
C:\Users\lenovo\.cache\chrome-devtools-mcp\chrome-profile
```

如果多个 MCP server 或多个 session 共用这个目录，Chrome profile 会被单实例锁占用，后启动的 session 可能报错：

```text
The browser is already running for ... chrome-profile. Use --isolated to run multiple browser instances.
```

## 2. 不能只裸用 `--isolated`

`--isolated` 可以让每个 MCP client session 使用独立临时 Chrome profile，避免 profile 锁冲突。
但裸用 `--isolated` 有长期运行风险：

- 旧 session 如果没有正常退出，旧 Chrome 实例可能继续存在；
- 新 session 再启动时可能再开一个新的 Chrome；
- 时间久了可能出现 Chrome 窗口或 `chrome.exe` 进程堆积；
- 临时 profile 通常只有浏览器正常关闭后才清理，不能替代 session 生命周期治理。

因此生产默认不应只是：

```toml
args = ["-y", "chrome-devtools-mcp@latest", "--isolated"]
```

而应升级为受管隔离模式。

## 3. 推荐目标模式

推荐目标模式：

```text
chrome-devtools = isolated-session-managed
```

含义：

1. 每个 Codex session 使用独立 Chrome profile；
2. 同一个 session 内尽量复用自己拥有的 Chrome；
3. 新 session 不复用旧 session 的临时 profile；
4. 启动前扫描并清理明确 stale 的旧受管实例；
5. 设置最大活跃实例数量，防止长期堆积；
6. 只管理命令行或 lease 记录中明确属于 `chrome-devtools-mcp` 受管 profile 的 Chrome；
7. 不关闭、不杀掉、不接管用户日常 Chrome。

## 4. 受管 wrapper 设计

建议未来不要让 Codex 直接调用裸 `npx chrome-devtools-mcp@latest`，而是让 `config.toml` 指向用户级 wrapper：

```toml
[mcp_servers.chrome-devtools]
command = "powershell"
args = [
  "-NoProfile",
  "-ExecutionPolicy", "Bypass",
  "-File",
  "C:\\Users\\lenovo\\.codex\\tools\\chrome-devtools-mcp-managed.ps1",
  "--mode", "isolated-session"
]
```

wrapper 内部再启动：

```powershell
npx -y chrome-devtools-mcp@latest --isolated
```

或在需要可审计 profile 路径时使用 session 专属 `--user-data-dir`。

## 5. Lease 记录

每个受管 Chrome DevTools MCP 实例启动时写入 lease 文件。
建议目录：

```text
C:\Users\lenovo\.codex\state\chrome-devtools-mcp\leases\
```

每个 lease 至少记录：

- `lease_id`；
- `project_path`；
- `codex_session_id` 或可用的 session namespace；
- `mcp_server_pid`；
- `chrome_root_pid`；
- `user_data_dir`；
- `started_at`；
- `last_seen_at`；
- `mode`：`isolated-session` / `project-profile`；
- `status`：`active` / `stale` / `cleaned` / `unknown`；
- `owner_command_hash` 或启动命令摘要；
- `cleanup_policy`：安全清理策略与 lease 记录留存规则。

## 6. 启动前清理规则

新实例启动前执行只读扫描：

1. 读取 lease 目录；
2. 检查 `mcp_server_pid` 是否仍存在；
3. 检查 `chrome_root_pid` 是否仍存在；
4. 检查 Chrome command line 是否包含受管 profile 路径；
5. 检查 lease 是否超过 stale TTL；
6. 只在 owner 进程不存在且 Chrome 明确属于受管 profile 时清理；
7. 清理后把 lease 标记为 `cleaned`，不要直接删除证据。

禁止行为：

- 不按 command line 或 lease 归属直接杀所有 `chrome.exe`；
- 不清理普通 Chrome 用户 profile；
- 不清理不属于当前受管目录的 Chrome；
- 不把 `--isolated` 当作生命周期管理机制。

## 7. 实例数量上限

建议设置：

```text
max_active_managed_instances = 3
stale_ttl_minutes = 120
```

当活跃受管实例超过上限时：

1. 优先报告并拒绝新开；
2. 或只清理确认 stale 的实例；
3. 不清理状态未知但仍可能活跃的实例；
4. 需要人工确认时，输出候选 lease 和 PID，不直接破坏。

## 8. 模式选择

### 8.1 普通 Codex 自动化调试

使用 `isolated-session-managed`。

适用：

- 本地网页调试；
- DOM / console / network 检查；
- 一次性 UI 验证；
- 多项目、多 session 并发。

### 8.2 需要保留登录态的项目

使用项目专属 profile：

```text
C:\Users\lenovo\.cache\chrome-devtools-mcp\profiles\<project-slug>
```

限制：

- 同一项目 profile 同一时间只能由一个 session 占用；
- 多 session 并发仍应使用 session 独立 profile；
- 登录态 profile 必须标记为长期 profile，禁止 stale cleanup 自动删除目录。

## 9. 验证与审计

后续实施时应新增检查脚本，至少验证：

- `config.toml` 不再裸用共享默认 `chrome-profile`；
- 受管 wrapper 存在；
- lease 目录存在且格式可读；
- cleanup 只匹配受管 profile；
- 普通 Chrome 不会被误杀；
- stale cleanup 会保留 receipt；
- 多 session 启动不会争抢同一个 `userDataDir`。

## 10. 当前结论

只用 `--isolated` 可以解决 profile 锁冲突，但会引入长期窗口/进程堆积风险。
长期推荐落地为：

```text
--isolated + session ownership lease + stale cleanup + max instance limit
```

这是多项目、多 session 调用独立 Chrome DevTools MCP 的生产级默认方向。
