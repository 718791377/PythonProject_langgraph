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

# LangGraph State Release Evidence Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Reject stale running LangGraph state after completed work and require explicit close, release, or handoff evidence.

## 来源方案

- automatic_orchestration_routing_enforcement_plan; codex_user_level_cross_session_durable_state_isolation_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 3。
- 阶段：Phase 4。
- 状态：本文件是 active 子 implementation_plan，但在本地 `main` 合入后仍必须等待用户确认，才能开始非文档实现。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：已实施并完成本地验证
阶段：Stage C 实施包
负责人会话：`codex-langgraph-state-release-evidence-20260530`
当前门禁：本地验证已完成，等待合入本地 main；远端发布仍不在范围内
Stage C 进入条件：用户于 2026-05-30 确认继续实施，且该子方案已在本地 `main`
最后更新：2026-05-30
<!-- CURRENT_STATUS_END -->

## 文件归属

- tools/langgraph_durable_orchestrator/*
- tools/check_durable_artifact_state_surfaces.py
- test/*langgraph*state*release*

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- .omx/state/langgraph
- LangGraph compatibility records

## 并行会话契约

- 本阶段最大并行 session 数：3。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add fixtures for completed, running, released, and handoff LangGraph states.
- [x] Update durable state checker to flag stale running state after completion.
- [x] Document safe backend-family handoff requirements.
- [x] Run durable state and LangGraph checks plus local gate.
<!-- TASK_BACKLOG_END -->

## 验证门禁

除非后续经确认的子方案更新给出更窄且有理由的命令列表，否则本地 `main` 合入前运行：

- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan anchors, size limits, registry entries, and bilingual pairs.
- `python tools/check_precommit_update_archive.py --root . --json` - reviews required existing-file updates, checker registration, and archive readiness before commit.
- `python tools/check_worktree_task_receipt.py --root . --json` - validates worktree claim and receipt lifecycle metadata.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs local MR review before local main integration.

## 验收标准

- 本地 `main` 合入后，用户已确认本子方案。
- active session claim 在写入工作开始前明确指向本子方案路径。
- 行为变更必须先有失败测试或 checker fixture。
- 治理文档、runtime helper、checker、测试和 CI 注册保持一致。
- 证据以轻量索引记录，不向本方案正文追加大型证据包。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-05-30 Stage C 实施：分支 `implement-langgraph-state-release-evidence-20260530` 新增结构化 LangGraph state-release fixtures，扩展 `tools/check_durable_artifact_state_surfaces.py` 以拒绝 completed work 仍处于 `running` state 以及缺失 release/handoff 字段的情况，登记 `test/check_langgraph_state_release_evidence.test.py`，并记录 backend-family handoff 要求；最终 local-main commit 将在集成后记录。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
