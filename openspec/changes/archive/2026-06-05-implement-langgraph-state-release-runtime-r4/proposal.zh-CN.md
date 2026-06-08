# 变更：实现 LangGraph State Release Runtime R4

## 为什么

Stage C 的 checker 已经可以拒绝 completed work 之后仍停留在 `running` 的 LangGraph state，但 runtime 仍缺少真正的 close、release、handoff helper 来写入 repo-local 证据。没有该 helper 时，操作者只能依赖手工改状态或 chat-only note 来证明已完成 LangGraph thread 不再 active。

## 改什么

- 增加 repo-local LangGraph release helper command，用于 close、release 或 handoff tracked thread。
- 在 `.omx/state/langgraph/store/releases/` 下持久化结构化 release receipt。
- 更新 thread state 与 backend projection，确保 completed work 不再报告 `running`。
- 增加 runtime 测试覆盖 close、release、handoff、receipt 字段以及 inspect/status projection。
- 更新 active implementation plan 的 Stage D/R4 状态。

## 影响

- 影响 `tools/langgraph_durable_orchestrator/` runtime 与 CLI surface。
- 新增 Python regression coverage，并登记到 CI manifest。
- 归档时把 reusable release-runtime requirement 推进到 LangGraph durable backend stable spec。
- 除非用户明确授权，本变更不包含远端发布。
