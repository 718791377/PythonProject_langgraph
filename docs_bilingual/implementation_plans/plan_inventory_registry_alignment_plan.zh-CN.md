---
doc_id: plan_inventory_registry_alignment_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/plan_inventory_registry_alignment_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 0
batch: 1
confirmation_required: true
---

# Plan Inventory Registry Alignment Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Inventory active implementation plans, registry entries, stable anchors, and evidence-index health before parallel execution starts.

## 来源方案

- multi_plan_parallel_session_orchestration_plan; implementation_plan_confirmation_gate

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 1。
- 阶段：Phase 0。
- 状态：本文件是 active 子 implementation_plan，但在本地 `main` 合入后仍必须等待用户确认，才能开始非文档实现。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：active
阶段：Phase 0 收口已合入本地 `main`；本文件继续作为盘点对齐子方案保持 active
责任会话：`phase0-plan-index-closure-20260530`
当前门禁：Phase 0 已无待执行的本地 `main` 合入；后续编辑必须使用新的 claim/worktree，通过本地门禁，合入本地后停在远端发布门。
Stage C 进入条件：用户已确认 Phase 0 必须先于 Phase 2 完成；本次收口记录盘点结果。
最后更新：2026-06-07
<!-- CURRENT_STATUS_END -->

## 文件归属

- docs_bilingual/docs_registry.yaml
- docs_bilingual/implementation_plans/*
- tools/implementation_plan_size_baseline.json

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- docs_bilingual/docs_registry.yaml
- tools/check_implementation_plan_rules.py

## 并行会话契约

- 本阶段最大并行 session 数：2。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] 本子方案合入本地 main 后已获得用户确认。
- [x] 读取 registry，并生成 implementation-plan pair 的机器可检查盘点。
- [x] 检查缺失 registry 条目、缺失稳定锚点和缺失 evidence index 引用的覆盖情况。
- [x] 仅修复本子方案负责的 registry 或 anchor 问题；本次未发现阻塞性 registry 或双语配对缺陷。
- [x] 运行 implementation-plan rules、precommit update/archive review、local gate 和 local MR review。
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
- 2026-06-07 本地合入状态刷新：分支 `phase0-plan-index-closure-20260530` 已合入本地 `main`；父方案状态已同步，因此 Phase 0 不再描述为等待本地合入。
- 2026-05-30 完整提交流程对齐：Phase 0 盘点结果保持有效；本次仅把后续 session 读取和合入语义对齐为父方案可选、子方案自负责、`local-main-retire.lock` 串行本地 `main` 写入。
- 2026-05-30 Phase 0 盘点收口：机器可读证据记录在 `docs_bilingual/implementation_evidence/phase0_plan_inventory_registry_alignment_20260530.json`；可读证据记录在 `docs_bilingual/implementation_evidence/phase0_plan_inventory_registry_alignment_20260530.md` 与 `docs_bilingual/implementation_evidence/phase0_plan_inventory_registry_alignment_20260530.zh-CN.md`。盘点结果为 59 个 implementation-plan registry 条目、52 个 active 条目、无缺失登记路径、无缺失双语 companion 路径。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
