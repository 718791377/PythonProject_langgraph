---
doc_id: prompt_independent_activation_parity_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/prompt_independent_activation_parity_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 4
batch: 3
confirmation_required: true
---

# Prompt Independent Activation Parity Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Ensure automatic collaboration routing does not depend on the user saying parallel, experts, subagents, OMX, or LangGraph.

## 来源方案

- automatic_orchestration_routing_enforcement_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 3。
- 阶段：Phase 4。
- Status: implementation has been confirmed, completed through checker, fixture, documentation, and CI-manifest updates on local `main`, and this file now records the closeout package.
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented and locally validated
Stage: Stage C closeout package
Owner session: `codex-close-prompt-independent-activation-parity-20260531`
Current gate: closeout documentation pending local validation, local commit, and local `main` integration; remote publication remains out of scope
Stage C entry condition: satisfied on 2026-05-30 after user confirmation
Last updated: 2026-05-31
<!-- CURRENT_STATUS_END -->

## 文件归属

- tools/check_role_routing_directive_evidence.py
- tools/check_orchestration_collaboration_evidenceguard.py
- test/*prompt_independent*

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- activation policy docs
- role routing checker

## 并行会话契约

- 本阶段最大并行 session 数：3。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add fixtures for qualified tasks with and without user collaboration keywords.
- [x] Require concrete blockers instead of missing-user-reminder excuses.
- [x] Update checker messages and policy docs.
- [x] Run role routing and orchestration evidence checks plus local gate.
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
- 2026-05-31 Stage C closeout: branch `close-prompt-independent-activation-parity-20260531` records that prompt-independent activation parity is implemented through the role-routing checker, collaboration evidence guard, prompt-independent fixtures, activation-policy documentation, CI manifest registration, and local validation gates; final local-main commit is recorded in the assistant response and local git history.
- 2026-05-30 Stage C implementation: added qualified prompt-independent parity fixtures, missing-reminder negative fixture handling, role evidence rejection, policy doc notes, and CI manifest registration; final validation evidence is recorded in local gate and commit output.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
