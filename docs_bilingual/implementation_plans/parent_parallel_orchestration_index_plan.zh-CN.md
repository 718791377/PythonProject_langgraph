---
doc_id: parent_parallel_orchestration_index_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/parent_parallel_orchestration_index_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 0
batch: 1
confirmation_required: true
---

# Parent Parallel Orchestration Index Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Keep the parent phase map, child-plan registry, dependency order, and session-limit table current while child plans are created and executed.

## 来源方案

- multi_plan_parallel_session_orchestration_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 1。
- 阶段：Phase 0。
- 状态：本文件是 active 子 implementation_plan，但在本地 `main` 合入后仍必须等待用户确认，才能开始非文档实现。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
阶段：Phase 0 已收口；当前作为父方案族索引维护子方案继续 active
责任会话：`codex-align-complete-flow-parent-plans-20260530`，用于本次父方案族完整提交流程对齐。
当前门禁：更新父方案当前状态、Phase 2+ 准入说明、子方案状态索引和所有子方案的 local-main 合入语义；通过 checker 后提交并合入本地 `main`，然后停在远端发布门。
<!-- CURRENT_STATUS_END -->

## 文件归属

- docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
- docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
- docs_bilingual/docs_registry.yaml entries for child plans

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- parent plan pair
- docs_bilingual/docs_registry.yaml

## 并行会话契约

- 本阶段最大并行 session 数：2。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] 2026-05-30 完整提交流程对齐：维护父方案索引，把父方案族子方案从固定 leader 合入语义更新为 `local-main-retire.lock` 保护的 session-owned self-retire。
- [x] 本子方案本地 main 合入后已获得用户确认。
- [x] 为父方案加入二层级架构图，并明确本索引维护方案是同级子方案，不是二级父方案。
- [x] 吸收 Pi family / oh-my-pi / CLI harness reference-only 边界到父级编排方案。
- [x] 登记 Phase 1A complete-flow scheduler/ROB 子方案，并把它作为 Batch 1 early-foundation 补充。
- [x] 向父方案加入紧凑 child-plan 状态表。
- [x] 记录 phase 与 child plan 之间的依赖边，且不复制完整证据包。
- [x] 验证父方案状态可以只通过稳定锚点更新。
- [x] 运行 implementation-plan rules 和 local MR review。
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
- 2026-05-30 完整提交流程对齐：`codex-align-complete-flow-parent-plans-20260530` 认领本索引子方案，更新父方案和子方案状态；ROB entry `rob-align-complete-flow-parent-plans-20260530` 记录本地候选包。
- 2026-05-30 Phase 0 索引收口：已更新父方案当前状态、Phase 0/Phase 1 完成证据、紧凑 child-plan 状态索引、依赖/准入说明和 Phase 2 门禁条件。
- 2026-05-29 索引补充：登记 Phase 1A complete-flow scheduler/ROB 子方案，保持其为父方案的同级 child implementation_plan。
- 2026-05-28 文档治理更新：main Codex leader session 认领本索引维护子方案，用于更新父方案层级架构图和 Pi/harness reference-only 边界；commit 记录在本地 git 历史中。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
