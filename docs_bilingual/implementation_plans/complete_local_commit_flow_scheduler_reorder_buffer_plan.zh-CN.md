---
doc_id: complete_local_commit_flow_scheduler_reorder_buffer_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/complete_local_commit_flow_scheduler_reorder_buffer_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 1
phase_label: Phase 1A
batch: 1
priority: early-foundation
confirmation_required: true
---

# 完整本地提交流程调度器重排序缓冲实施方案（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

通过允许 session 在隔离 worktree 中并行执行、但要求 main Codex leader 按 ROB 风格串行 retire 到本地 `main`，让多 session 本地提交流程变得安全。

## 来源方案

- multi_plan_parallel_session_orchestration_plan
- `完整提交流程.md` - 记录完整本地提交流程的 ROB 并发治理规则。 中的完整本地提交流程治理
- portable_no_backend_parallel_session_plan
- worktree_receipt_claim_lifecycle_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和后续 runtime/checker 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 1 补充子方案。
- 阶段：Phase 1A，归入 Phase 1 施工安全底座。
- 状态：本文件是 active 子 implementation_plan。本包只创建治理方案；runtime/checker 实现必须等待后续用户确认。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：active
阶段：Stage C runtime/checker 实现已合入本地 main 并已验证
责任会话：main Codex leader session
当前门禁：Phase 1 收口记录提交并合入本地 main 后，远端发布已获授权
实现进入条件：已由用户在 2026-05-29 确认继续实施本子 implementation plan
最后更新：2026-05-29
<!-- CURRENT_STATUS_END -->

## 文件归属

当前文档治理包拥有：

- `完整提交流程.md` - 记录完整本地提交流程的 ROB 并发治理规则。
- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md` - 记录父方案 Phase 1A 位置和调度依赖。
- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md` - 同步中文父方案对照版。
- `docs_bilingual/implementation_plans/complete_local_commit_flow_scheduler_reorder_buffer_plan.md` - 定义本子方案英文主版。
- `docs_bilingual/implementation_plans/complete_local_commit_flow_scheduler_reorder_buffer_plan.zh-CN.md` - 定义本子方案中文对照版。
- `docs_bilingual/docs_registry.yaml` - 登记本双语子方案。

后续 runtime/checker 实现可能拥有：

- `tools/commit_reorder_buffer.py` - 后续管理 ROB entry 预测、入队、状态、退休和 flush。
- `tools/check_commit_reorder_buffer.py` - 后续验证 ROB 就绪、热点 fence 和退休证据。
- local CI 或 local MR review 接线
- ROB entry 状态、热点 fence、串行 retire 的聚焦测试

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- 完整本地提交流程政策
- 父级编排方案中英文对
- docs registry
- 后续 ROB helper/checker 脚本
- claim 与 receipt lifecycle schema 表面

## 调度模型

本子方案把调度器和 CPU 提交原则转换为仓库治理：

- Reorder Buffer：候选包在进入 local `main` 前先缓冲。
- Out-of-order execution：写集互不重叠的 session 可以乱序完成。
- In-order retirement：local `main` 集成必须由 leader 串行执行。
- Scoreboarding / Tomasulo 就绪判断：依赖、claim、receipt、写集和 gate 共同决定 entry 是否 ready。
- Load/store queue 与 memory fence：共享治理文件和 schema 表面强制串行化。
- Branch prediction / speculation：session 开始前预测写集和依赖；预测失败则 blocked、flushed、split 或 requeued。
- Backpressure / priority aging：gate 失败或 retire queue 堆积时降低并发，长期 ready entry 必须显式暴露。
- Checkpoint / rollback：每次 retire 都需要 rollback ref 和 evidence。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] 把本子方案放入 Phase 1A，而不是靠后的阶段或新增 Phase 8。
- [x] 更新 `完整提交流程.md`，加入 ROB 风格多 session 执行和串行 retire 规则。
- [x] 更新父级编排方案中英文对，加入 Phase 1A 子方案和 Batch 1 补充状态。
- [x] 在 `docs_bilingual/docs_registry.yaml` 登记本双语子方案。
- [x] 把 portable no-backend session 和 worktree receipt lifecycle 方案标为下游消费者。
- [x] 本地 main 合入后先确认本子方案，再进入 runtime/checker 实现。
- [x] 定义 ROB entry schema 和非 Git 运行态目录，默认 `.omx/commit-rob/`。
- [x] 实现 `tools/commit_reorder_buffer.py` 命令：`predict`、`enqueue`、`status`、`retire`、`flush`。
- [x] 实现 `tools/check_commit_reorder_buffer.py`，检查 claim 唯一性、热点 fence、ready entry 可 retire 和 retired evidence。
- [x] 增加聚焦测试：互不重叠 ready entry、热点冲突、分支预测失败、gate 失败和 backpressure。
- [x] runtime helper 实现后，把 checker 接入 local gate 或 local MR review。
<!-- TASK_BACKLOG_END -->

## 验证门禁

除非后续经确认的更新给出更窄且有理由的命令列表，否则本地 `main` 合入前运行：

```powershell
python tools/check_precommit_update_archive.py --root . --json
python tools/check_implementation_plan_rules.py --root . --json
python tools/check_local_flow_scripted_enforcement.py --root . --json
```

如果当前分支可用，还应在本地 main 合入前运行 shared local gate 和 local MR review。

## 验收标准

- `完整提交流程.md` - 记录完整本地提交流程的 ROB 并发治理规则。 说明 ROB 缓冲、乱序执行、串行 retire、热点 fence、分支预测失败处理、backpressure 和 rollback evidence。
- 父方案把本子方案列入 Phase 1A / Batch 1 补充安全底座工作。
- portable no-backend 与 receipt lifecycle 方案引用本方案作为上游调度契约。
- 英文主版保持 ASCII-only，中文对照版已登记。
- 本地 main 合入后、用户确认本子方案前，不进入 runtime/checker 实现。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-05-29 runtime/checker 实现：新增 `tools/commit_reorder_buffer.py`、`tools/check_commit_reorder_buffer.py`、聚焦测试、local gate manifest 登记和 OpenSpec guard 接线；聚焦测试、Python manifest、precommit/update-archive、OpenSpec guard JSON、local MR review 与 local gate 已通过；已在 `4479593` 合入本地 `main`，rollback ref 为 `refs/backup/local-main/20260529-1259-before-complete-flow-rob-runtime`，合入后 local gate 已通过，ROB entry 已 retired。
- 2026-05-29 文档治理包：创建 active Phase 1A 子方案，并更新 complete-flow、父方案和消费者方案引用；已在 `ebe5f69` 合入本地 `main`，随后才进入 runtime/checker 实现。
<!-- EVIDENCE_INDEX_END -->
