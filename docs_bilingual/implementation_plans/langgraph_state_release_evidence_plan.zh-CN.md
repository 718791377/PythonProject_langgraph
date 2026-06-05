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
状态：Stage D/R4 真实 runtime implementation 已完成并已归档；归档后本地门禁待重跑。
阶段：Stage D 真实 runtime package，已在 guarded local `main` 集成前完成 OpenSpec archive。
Owner session：`implement-langgraph-state-release-r4-20260605`。
当前门禁：重跑归档后的 precommit/local gates，然后通过 guarded local-main-first 集成；remote publication 仍未授权。
Stage D 入口条件：已由 2026-06-05 用户要求继续 `langgraph_state_release_evidence_plan` 至 R4 的消息满足。
OpenSpec 归档：`openspec/changes/archive/2026-06-05-implement-langgraph-state-release-runtime-r4/`。
本地 main 集成：提交、local gate 与 local MR review 通过后，经 `tools/complete_local_flow_to_remote_gate.py --execute` 待执行。
前置 Stage C 本地集成：已在 `32a5cfff3b977ba13ed6e215b4efb887679019b9` 完成；completed claim 保存在 `.omx/session-claims/completed/implement-langgraph-state-release-evidence-20260530.json`。
中文 companion refresh note：保留 local `main` 上的中文化清理结果；本次 R4 只叠加 runtime 完成与归档状态，不回退该中文修复。
Last updated：2026-06-05。
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

此前真实 runtime 缺口已由 Stage D/R4 包在当前 feature branch 中收口：runtime 现在提供 close、release 与 handoff 的显式 receipt，并把证据写出到 transient chat context 之外。在 guarded local `main` 集成完成前，本包应视为“已实现并已归档，但归档后本地门禁仍待通过”。

<!-- TASK_BACKLOG_START -->
- [x] Stage B：记录 stale running LangGraph state 必须释放或交接。
- [x] Stage B：把 release/handoff evidence 接入 durable artifact/state-surface 检查。
- [x] Stage C：把真实 runtime gap 明确为 pending release helper，而不是已完成 runtime。
- [x] Stage D real runtime：实现 LangGraph thread release helper，记录 thread id、backend family、previous state、release action、survivor queue 与 handoff target。
- [x] Stage D real runtime：实现 close/handoff receipts，防止 completed work 后继续留下 stale running state。
- [x] Stage D real runtime：增加 rollback/restore evidence，避免 release mistake 被隐式转换成 backend-family switch。
<!-- TASK_BACKLOG_END -->

## Stage D runtime completion（真实 runtime 完成项）

- [x] `release-thread` 支持 `close`、`release` 与 `handoff` actions，并把 release receipt 写入 `.omx/state/langgraph/store/releases/`。
- [x] `handoff` 要求 `handoff_target` 与 `reason`，避免无目标交接。
- [x] status / inspect / backend projections 暴露 release receipt evidence，供 checker 与冷启动读取。

## 验证门禁

- `python tools/check_durable_artifact_state_surfaces.py --root . --json` - 验证 durable artifact/state surfaces。
- `python tools/check_orchestration_collaboration_evidenceguard.py --root . --json` - 验证协同证据 guard。
- `python tools/check_precommit_update_archive.py --root . --json` - 执行提交前更新/归档检查。
- `python tools/run_openspec_guard.py --root .` - 执行 OpenSpec 与治理 guard。
- `tools/ci/local_gate.ps1` - 执行共享本地 CI gate。

## 验收标准

- 中文对照版说明为中文；保留必要技术名词、路径和 checker token。
- completed LangGraph work 没有 release/handoff evidence 时不得声明 running 或 completed runtime。
- R4 完成声明必须依赖 release helper、receipt projection 与测试证据，而不是只依赖对话说明。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 Stage D/R4 runtime implementation：branch `implement-langgraph-state-release-r4-20260605` 新增 `release-thread`，支持 `close`、`release` 与 `handoff`；receipt 写入 `.omx/state/langgraph/store/releases/`；status / inspect / backend records 暴露 release projections；`test/check_langgraph_state_release_evidence.test.py` 增加 runtime release-helper coverage；保留 rollback/restore 与 timeout release evidence，且不隐式切换 backend family。目标验证：`python test\check_langgraph_state_release_evidence.test.py` 与 `python tools\check_durable_artifact_state_surfaces.py --root . --json`。
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 将 LangGraph thread state release runtime helper 标记为 Stage D pending；当前只具备 state-release checker。
- 2026-05-31 本地 main 状态同步：记录 Stage C 实施已合入本地 `main`，集成提交为 `32a5cfff3b977ba13ed6e215b4efb887679019b9`，completed claim 已保存在 `.omx/session-claims/completed/implement-langgraph-state-release-evidence-20260530.json`，剩余门禁为显式远端发布批准。
- 2026-05-30 Stage C 实施：分支 `implement-langgraph-state-release-evidence-20260530` 新增结构化 LangGraph state-release fixtures，扩展 `tools/check_durable_artifact_state_surfaces.py` 以拒绝 completed work 仍处于 `running` state 以及缺失 release/handoff 字段的情况，登记 `test/check_langgraph_state_release_evidence.test.py`，记录 backend-family handoff 要求，并已在 `32a5cfff3b977ba13ed6e215b4efb887679019b9` 合入本地 `main`。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
