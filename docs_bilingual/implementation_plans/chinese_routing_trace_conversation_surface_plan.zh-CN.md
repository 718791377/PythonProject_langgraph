---
doc_id: chinese_routing_trace_conversation_surface_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/chinese_routing_trace_conversation_surface_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 4
batch: 3
confirmation_required: true
---

# 中文路由跟踪与更新计划会话表面实施方案

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

要求对话中面向用户展示的路由跟踪和更新计划使用中文字段名、中文说明和中文状态表达；保存版结构化 evidence 继续保留机器可读 ASCII 阈值、blocker token、schema key、文件名和命令参数。

## 来源方案

- `codex_governance_session_visibility_and_plan_lock_plan` - 定义中文会话可视化和 plan lock 治理。
- `automatic_orchestration_routing_enforcement_plan` - 定义自动路由证据和 activation parity 要求。
- `multi_plan_parallel_session_orchestration_plan` - 提供本 Phase 4 子方案族的父级上下文。

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 3。
- 阶段：Phase 4。
- 状态：本文件是 active 子 implementation_plan；本次用户已确认更新本子方案和父方案，但后续非文档 runtime 实现仍必须再次确认具体实现切片。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：active
阶段：Stage B 子方案治理修订
责任会话：`codex-chinese-routing-updated-plan-20260530`
当前门禁：本次只更新父子 implementation_plan；后续 runtime/checker 实现必须由被确认的实施切片继续执行
Stage C 进入条件：用户明确确认本子 implementation_plan 的非文档实现范围
最后更新：2026-05-30
<!-- CURRENT_STATUS_END -->

## 文件归属

- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md` - 声明 Phase 4 范围的英文父方案。
- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md` - Phase 4 范围的中文对照父方案。
- `docs_bilingual/implementation_plans/chinese_routing_trace_conversation_surface_plan.md` - 本切片的英文主版子方案。
- `docs_bilingual/implementation_plans/chinese_routing_trace_conversation_surface_plan.zh-CN.md` - 本切片的中文对照子方案。

后续 runtime/checker 实现切片可扩展到：

- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` - 后续英文治理示例目标。
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md` - 后续中文治理示例目标。
- `tools/check_orchestration_collaboration_evidenceguard.py` - 后续会话表面 fixture 的 checker 目标。
- `test/*routing_trace_chinese*` - 后续验证用户可见路由跟踪文案的测试。
- `test/*updated_plan_chinese*` - 后续验证用户可见更新计划文案的测试。

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- 用户可见路由跟踪文案
- 用户可见更新计划文案
- routing evidence schema
- plan-progress evidence schema

## 并行会话契约

- 本阶段所有 eligible 子方案均可按 Work-Conserving 规则并行。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠，或已取得相应 hotspot lease 时，才允许并行实施。
- 本地 `main` 写入仍然串行，由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] 更新父方案 Phase 4，使中文会话表面同时覆盖路由跟踪和更新计划。
- [x] 更新本子方案目标、范围、热点、任务和验收标准。
- [x] 同步英文 ASCII 主版和中文对照版。
- [ ] 后续 runtime/checker 实现：增加 fixture，拒绝英文-only 用户可见路由跟踪。
- [ ] 后续 runtime/checker 实现：增加 fixture，拒绝英文-only 用户可见更新计划。
- [ ] 后续治理实现：更新 activation policy 示例，使对话示例使用“路由跟踪”和“更新计划”。
- [ ] 后续验证：运行 routing evidence checker、implementation-plan checker、local gate 和 local MR review。
<!-- TASK_BACKLOG_END -->

## 验证门禁

除非后续经确认的子方案更新给出更窄且有理由的命令列表，否则本地 `main` 合入前运行：

- `python tools/check_implementation_plan_rules.py --root . --json` - 验证 implementation-plan 锚点、体积限制、registry 登记和双语配对。
- `python tools/check_precommit_update_archive.py --root . --json` - 提交前复核必须同步的既有文件、checker 注册和 archive 状态。
- `python tools/check_worktree_task_receipt.py --root . --json` - 验证 worktree claim 和 receipt 生命周期元数据。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - 运行共享本地 CI gate。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_mr_review.ps1` - 本地 `main` 合入前运行 local MR review。

## 验收标准

- 父方案 Phase 4 明确覆盖用户可见路由跟踪和用户可见更新计划。
- 本子方案明确区分用户可见中文表面与保存版机器可读 ASCII evidence。
- 对话中不得出现英文-only `Routing trace:` 作为用户可见标题；应使用“路由跟踪”。
- 对话中不得出现英文-only `Updated Plan` 作为用户可见标题；应使用“更新计划”。
- 英文工具名、文件名、schema key、阈值 token、blocker token 和 CLI 参数允许保持 ASCII。
- Evidence 以轻量索引记录，不向本方案正文追加大型证据包。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-05-30 Phase 4 中文会话表面治理更新：分支 `chinese-routing-updated-plan-20260530` 更新父方案和本子方案，把用户可见中文要求从路由跟踪扩展到路由跟踪与更新计划；本次只更新 implementation_plan，不进入 runtime/checker 实现。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
