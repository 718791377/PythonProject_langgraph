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
Status: implemented-local
Status: R6 live-executed
Stage: R6 live-runtime receipt coverage package for `langgraph_state_release_evidence_plan`.
Owner session: `implement-multi-plan-family-r6-live-runtime-20260611` updates the strict parent-family checker; existing accepted receipts remain the live runtime evidence source.
R6 evidence: `.omx/r6-live-runtime/receipts/` contains accepted `live-executed` evidence for lane `langgraph-state-release-evidence`, validated by `tools/check_r6_live_runtime_receipts.py --require-coverage` and `tools/check_multi_plan_family_r6_live_runtime.py --require-coverage`.
Runtime boundary: this status update performs no browser/GUI action, no WXWork message send, no harness job, no Spec Kit apply, no user-level config mutation, and no remote publication; it reconciles the plan with accepted hash-only/redacted R6 receipts.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-11
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
- 2026-06-07 R5 active-candidate gate：branch `implement-r5-runtime-governance-batch-20260607` 为 LangGraph state release evidence 增加共享 active-candidate receipt validation。证据必须包含 authorization receipt、owner lease、target/action allowlist、timeout release、redacted transcript、rollback pointer/readiness、cleanup evidence，并带有按 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` 记录的 authority decision 以及 `remote_publication_mutated=false`。聚焦验证：`python test\check_r5_active_candidate_receipts.test.py` 以及 OpenSpec verification report 中列出的 lane-specific focused tests。本 package 不执行真实 user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action，也不执行 remote mutation。
- 2026-06-05 Stage D/R4 runtime implementation：branch `implement-langgraph-state-release-r4-20260605` 新增 `release-thread`，支持 `close`、`release` 与 `handoff`；receipt 写入 `.omx/state/langgraph/store/releases/`；status / inspect / backend records 暴露 release projections；`test/check_langgraph_state_release_evidence.test.py` 增加 runtime release-helper coverage；保留 rollback/restore 与 timeout release evidence，且不隐式切换 backend family。目标验证：`python test\check_langgraph_state_release_evidence.test.py` 与 `python tools\check_durable_artifact_state_surfaces.py --root . --json`。
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 将 LangGraph thread state release runtime helper 标记为 Stage D pending；当前只具备 state-release checker。
- 2026-05-31 本地 main 状态同步：记录 Stage C 实施已合入本地 `main`，集成提交为 `32a5cfff3b977ba13ed6e215b4efb887679019b9`，completed claim 已保存在 `.omx/session-claims/completed/implement-langgraph-state-release-evidence-20260530.json`，剩余门禁为显式远端发布批准。
- 2026-05-30 Stage C 实施：分支 `implement-langgraph-state-release-evidence-20260530` 新增结构化 LangGraph state-release fixtures，扩展 `tools/check_durable_artifact_state_surfaces.py` 以拒绝 completed work 仍处于 `running` state 以及缺失 release/handoff 字段的情况，登记 `test/check_langgraph_state_release_evidence.test.py`，记录 backend-family handoff 要求，并已在 `32a5cfff3b977ba13ed6e215b4efb887679019b9` 合入本地 `main`。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
