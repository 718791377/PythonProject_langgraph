# Design: 旧会话兼容策略

## 决策

保留旧 `/resume` thread 的临时可用性，但将它们的权威级别放在当前仓库状态之下。

## 脚本支撑

该规则由已有仓库 checker 支撑：

- `tools/check_mcp_router_scope_policy.py` 验证 Codex 直连 MCP 范围。
- `tools/check_windows_cleanup_output_control.py` 验证 wrapped launch 清理输出控制，且不需要禁用 `omx_*` server。
- `tools/check_session_ownership_claims.py` 在可写治理工作前验证当前会话归属。

## 回滚

该变更只修改文档和 registry（注册表）。回滚该提交即可移除兼容规则，不会触碰用户级 Codex 配置。
