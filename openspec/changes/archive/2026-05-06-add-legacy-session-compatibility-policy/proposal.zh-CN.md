# Proposal: 增加旧会话兼容策略

## 摘要

记录较早的 Codex `/resume` thread 可以临时继续使用，但只能作为 compatibility-scoped sessions（兼容范围会话），不能覆盖当前治理、直连 MCP 策略或当前本地 Git 状态。

## 范围

- 更新 startup 和 instruction surfaces（启动与指令表面）。
- 更新 MCP scope policy（MCP 范围策略）和 launcher payload policy（启动器载荷策略）。
- 更新 multi-session worktree isolation policy（多会话 worktree 隔离策略）。
- 增加 stable OpenSpec requirements（稳定 OpenSpec 需求），约束旧会话兼容和 scoped MCP workarounds（限定范围 MCP 绕过）。
- 在 script-backing registry（脚本支撑注册表）中登记该 safety rule（安全规则）。

## 非目标

- 不全局禁用直连 `omx_*`、`chrome-devtools` 或 `pencil` MCP server。
- 不在本仓库变更中编辑 `C:\Users\lenovo\.codex\config.toml`，该路径是用户级 Codex 配置文件。
- 不让旧会话成为新治理工作的权威来源。
