# Codex 平台项目画布

本文是 Codex CLI 个人开发者生产级持久化团队平台的轻量对齐工件。它不替代白皮书、MRD、implementation plan、OpenSpec 或 release evidence。它遵循 `Business Management/` 综合：让平台有意保持小、以机制驱动、用 outcome 衡量，并保持 repo-local。

## 来源与过程边界

当前画布派生自 `fresh_source_reading_evidence.zh-CN.md` 记录的 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260614` 证据边界。当画布进入执行授权时，应在相关 OpenSpec change、implementation plan 或生命周期文档中，把受影响层级展开为“输入 / 工具与技术 / 输出”，而不是把画布本身当成完整交付记录。

## 目的

建设个人生产级 Codex CLI 持久化团队平台，让一个维护者可以跨多个仓库工作，同时不丢失上下文、不混用 repo-local durable truth，也不破坏 native Codex。

## 价值假设

如果 startup context、worktree ownership、OpenSpec governance、release gates、rollback evidence 和 durable-lane selection 都可见且有脚本支撑，那么个人维护者就能更安全地跨项目使用 native Codex、`subagent`、`native_omx` 和 `langgraph`。

## 干系人

- user/operator：决定 release timing 和 approval gates 的用户或操作者。
- current main Codex session：当前主 Codex 会话，承担 leader 职责。
- native `subagent` roles：提供有边界 expert bursts 的原生子代理角色。
- optional durable lanes：可选持久化通道，例如 `native_omx` 和 `langgraph`。
- downstream project maintainers：下游项目维护者，以及未来冷启动会话。

## 边界

- native Codex 保持基础层。
- user-level helpers 是安装产物，不是 repo-local durable truth。
- 每个下游项目保留自己的 OpenSpec tree、Git history、release facts 和 `.omx/state/` directory。
- 长期 production durable-team plan 仍保持 draft，直到具体 release slices 通过 OpenSpec 被提升。

## 第一批价值增量

- 简短 startup summaries 和 read orders，让冷启动会话能恢复上下文。
- checker-backed safety rules，不只依赖 prompt reminders。
- worktree 和 session-ownership rules，减少多会话串台。
- 在启动任何 durable team 前，先做 read-only state inspection。
- release slices 保留 native Codex rollback paths。

## 风险

- hidden automation 可能被误当成 governance。
- shared user-level helpers 可能被误当成 shared durable truth。
- 从 PMBOK 派生的 lifecycle language 如果不裁剪，会变成 paperwork。
- 如果不强制边界，下游项目事实可能泄漏进平台仓库。

## 交付方式

使用 hybrid delivery style：

- predictive gates 用于 runtime entrypoints、checkers、release evidence、rollback evidence 和 repository governance。
- adaptive discovery 用于不清楚的 orchestration behavior、新模板和 project-consumption feedback。
- small release slices 用于 implementation、validation 和 learning。

## 结果检查

release slice 只有改善至少一个下列 outcome 时才有价值：

- cold-start continuation success；
- operator status clarity；
- cross-session coordination quality；
- repo-local durable-truth safety；
- native Codex compatibility 和 rollback confidence；
- downstream adoption safety 和 feedback quality。
