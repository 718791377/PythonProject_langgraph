---
doc_id: langgraph_state_release_evidence_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/langgraph_state_release_evidence_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 4
batch: 3
confirmation_required: true
---

# LangGraph 状态释放证据方案

> **给 agentic workers：** 使用 `superpowers:executing-plans`。本方案只处理 LangGraph thread state release / handoff evidence，不负责启动新的 durable team。

## 目标

在已完成 work 后拒绝继续依赖陈旧的 running LangGraph state，并要求明确的 close、release 或 handoff evidence。

## 来源方案

- automatic_orchestration_routing_enforcement_plan；codex_user_level_cross_session_durable_state_isolation_plan
- 本方案是 `multi_plan_parallel_session_orchestration_plan` 的子方案，只约束 LangGraph 状态释放证据。

## 范围决策

- 必须区分 completed work、paused work、handoff work 与 stale running state。
- completed work 不得继续冒充 running graph。
- release/handoff 证据必须写在 repo-local `.omx/state/langgraph/` 或明确登记的 artifact path。
- 不改变官方 `langgraph` package 的安装位置。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local；已有 state-release checker 与治理文本，能够阻止无证据的 running-state 声明。
Current gate：保持本地检查、OpenSpec guard 与 local-main-first 集成；remote publication 关闭。
Runtime boundary：当前 repo-local checker 只验证证据，不会自动 close LangGraph thread，不会迁移 graph state，也不会替用户执行 release/handoff。
Runtime gap：若要自动完成 release/handoff，仍需 LangGraph thread state release runtime helper，写入 close/release/handoff receipt、thread id、artifact path、rollback/restore note 与 redaction status。
<!-- CURRENT_STATUS_END -->

## 文件归属

- `tools/langgraph_durable_orchestrator/*` - 承载 repo-local LangGraph durable orchestrator 源码。
- `tools/check_durable_artifact_state_surfaces.py` - 校验 LangGraph durable artifact 与 state surface。
- `test/*langgraph*state*release*` - 覆盖 LangGraph state release fixture 与行为。
- `.omx/state/langgraph/` 下的 fixture 或 evidence schema

## 热点串行规则

LangGraph compatibility records、selector、active backend record 和 `.omx/state/langgraph/` schema 变更必须串行。

## 并行会话契约

一个 session 可独占本 implementation_plan。其他 session 可并行处理 receipt、selector、readiness 或 smoke 方案，但不得同时改本方案的文件归属和共享 guard 注册。

## 任务清单

## Real Runtime Implementation Gap（真实 runtime 缺口）

现有工作是治理/checker/test，不是自动 release runtime。后续 runtime 包需要提供：

<!-- TASK_BACKLOG_START -->
- [x] Stage B：记录 stale running LangGraph state 必须释放或交接。
- [x] Stage B：把 release/handoff evidence 接入 durable artifact/state-surface 检查。
- [x] Stage C：把真实 runtime gap 明确为 pending release helper，而不是已完成 runtime。
<!-- TASK_BACKLOG_END -->

## Stage D pending runtime work（待实施真实 runtime）

- Stage D real runtime：实现 LangGraph thread close/release/handoff helper，写入 release receipt。
- Stage D real runtime：记录 thread id、checkpoint/artifact path、handoff target、timeout release、rollback/restore note 与 redaction status。
- Stage D real runtime：为 completed graph state 执行受限 smoke，并验证不会继续报告 running。

## 验证门禁

- `python tools/check_durable_artifact_state_surfaces.py --root . --json` - 验证 durable artifact/state surfaces。
- `python tools/check_orchestration_collaboration_evidenceguard.py --root . --json` - 验证协同证据 guard。
- `python tools/check_precommit_update_archive.py --root . --json` - 执行提交前更新/归档检查。
- `python tools/run_openspec_guard.py --root .` - 执行 OpenSpec 与治理 guard。
- `tools/ci/local_gate.ps1` - 执行共享本地 CI gate。

## 验收标准

- 中文对照版说明为中文；保留必要技术名词、路径和 checker token。
- completed LangGraph work 没有 release/handoff evidence 时不得声明 running 或 completed runtime。
- Stage D 前不声明自动 release helper 已经实现。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 将 LangGraph thread state release runtime helper 标记为 Stage D pending；当前只具备 state-release checker。
- 2026-05-31 Stage B evidence：已有 durable artifact/state-surface checker 约束 LangGraph state release evidence。
<!-- EVIDENCE_INDEX_END -->
