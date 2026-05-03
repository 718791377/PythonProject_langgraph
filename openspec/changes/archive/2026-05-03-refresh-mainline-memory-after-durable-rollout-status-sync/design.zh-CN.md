## 设计

这是 handoff refresh change。它只更新 startup-facing memory text；不修改 runtime code、生成到用户级的 helper、durable state 或 MCP configuration。

刷新后的摘要应让冷启动会话清楚看到三件事：

1. 最新发布 mainline 已包含 Codex direct browser/design MCP policy 和 durable rollout plan status-sync archive。
2. MR 5 helper mirror source-of-truth 工作已经完成，不得再作为下一步 durable-state slice 重新打开。
3. 任何 MR 6 readiness 或 routing hookup 都必须在 ownership precheck 后作为单独命名的 OpenSpec change 打开，因为本 change 只做 memory refresh。

如果另一个 active session 拥有 broad `openspec/specs` 范围，则本 change 的 archive 有意延后。只有在后续明确串行归档时，短暂发布一个 active 且 complete 的 change 才是可接受的中间状态。
