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

# Routing trace 与 Updated Plan 会话表面稳定性实施方案

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

要求对话中面向用户展示的固定标签保持为 `Routing trace` 和 `Updated Plan`，不得翻译成中文标题；标签下的解释性内容可以使用中文。`Updated Plan` 必须继续保持复选框/状态清单语义，不能改成纯自然语言段落；保存版结构化 evidence 继续保留机器可读 ASCII 阈值、blocker token、schema key、文件名和命令参数。

## 来源方案

- `codex_governance_session_visibility_and_plan_lock_plan` - 定义会话表面可视化和 plan lock 治理。
- `automatic_orchestration_routing_enforcement_plan` - 定义自动路由证据和 activation parity 要求。
- `multi_plan_parallel_session_orchestration_plan` - 提供本 Phase 4 子方案族的父级上下文。

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 3。
- 阶段：Phase 4。
- 状态：本子 implementation_plan 已完成固定英文标签和 `Updated Plan` 清单语义的 runtime/checker 切片；本文现在记录最后一个验证清单项的收口包。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：implemented and locally validated
阶段：Stage C 收口包
责任会话：`codex-close-chinese-routing-trace-conversation-surface-plan-20260531`
当前门禁：收口文档等待本地校验、本地提交、local MR review、本地 `main` 集成，并在远端发布门停止
Stage C 进入条件：固定标签 runtime/checker 切片已合入本地 `main`，条件已满足；本包关闭剩余验证清单项
最后更新：2026-05-31
<!-- CURRENT_STATUS_END -->

## 文件归属

- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md` - 声明 Phase 4 范围的英文父方案。
- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md` - Phase 4 范围的中文对照父方案。
- `docs_bilingual/implementation_plans/chinese_routing_trace_conversation_surface_plan.md` - 本切片的英文主版子方案。
- `docs_bilingual/implementation_plans/chinese_routing_trace_conversation_surface_plan.zh-CN.md` - 本切片的中文对照子方案。

本次 runtime/checker 实现切片同时拥有：

- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` - 英文治理示例目标。
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md` - 中文治理示例目标。
- `tools/check_orchestration_collaboration_evidenceguard.py` - 会话表面 fixture 的 checker 目标。
- `test/fixtures/orchestration_prompt_independent_collaboration_parity/conversation_surface_*` - 验证固定标签和清单语义的 fixture。

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- 用户可见 `Routing trace` 标签和解释文案
- 用户可见 `Updated Plan` 标签与复选框/状态清单语义
- routing evidence schema
- plan-progress evidence schema

## 并行会话契约

- 本阶段所有 eligible 子方案均可按 Work-Conserving 规则并行。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠，或已取得相应 hotspot lease 时，才允许并行实施。
- 本地 `main` 写入仍然串行，由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] 更新父方案 Phase 4，使会话表面同时覆盖 `Routing trace` 和 `Updated Plan`。
- [x] 更新本子方案目标、范围、热点、任务和验收标准。
- [x] 同步英文 ASCII 主版和中文对照版。
- [x] 记录固定 `Routing trace` 标签不得替换为中文标题。
- [x] 记录固定 `Updated Plan` 标签不得替换为中文标题。
- [x] 增加 fixture，拒绝把固定标签替换为本地化标题，并拒绝纯文本 `Updated Plan` 输出。
- [x] 运行 routing evidence checker、implementation-plan checker、local gate 和 local MR review。
<!-- TASK_BACKLOG_END -->

## 验证门禁

除非后续经确认的子方案更新给出更窄且有理由的命令列表，否则本地 `main` 合入前运行：

- `python tools/check_implementation_plan_rules.py --root . --json` - 验证 implementation-plan 锚点、体积限制、registry 登记和双语配对。
- `python tools/check_precommit_update_archive.py --root . --json` - 提交前复核必须同步的既有文件、checker 注册和 archive 状态。
- `python tools/check_worktree_task_receipt.py --root . --json` - 验证 worktree claim 和 receipt 生命周期元数据。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - 运行共享本地 CI gate。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - 本地 `main` 合入前运行 local MR review。

## 验收标准

- 父方案 Phase 4 明确覆盖固定用户可见 `Routing trace` 和 `Updated Plan` 表面。
- 本子方案明确区分用户可见固定标签表面与保存版机器可读 ASCII evidence。
- 对话中必须保留 `Routing trace` 作为用户可见路由决策标签；解释内容可以使用中文。
- 对话中必须保留 `Updated Plan` 作为用户可见计划进度标签。
- `Updated Plan` 必须保留复选框/状态清单语义，例如复选框行或 pending / in_progress / completed 项，不能被替换为普通段落。
- 英文工具名、文件名、schema key、阈值 token、blocker token 和 CLI 参数允许保持 ASCII。
- Evidence 以轻量索引记录，不向本方案正文追加大型证据包。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-05-31 Stage C 收口：分支 `close-chinese-routing-trace-conversation-surface-plan-20260531` 将已实现的固定 `Routing trace` 与 `Updated Plan` 会话表面契约的最后验证清单项记录为完成；最终 local-main commit 与验证证据记录在 assistant 回复和本地 git 历史中。
- 2026-05-30 实施基线：本地 `main` 已包含 `implement-routing-updated-plan-fixed-labels-20260530c` 中的 fixed-label runtime/checker 包，包括稳定 `Routing trace` 和 `Updated Plan` 标签以及清单语义的 checker/fixture 覆盖。
- 2026-05-30 固定标签修正：用户确认 `Routing trace` 和 `Updated Plan` 保持英文用户可见标签，`Updated Plan` 保持清单语义；本切片更新父子方案约束，并增加 checker/fixture 覆盖。
- 2026-05-30 Phase 4 会话表面治理更新：分支 `chinese-routing-updated-plan-20260530` 曾把会话表面范围从 routing trace 扩展到 updated plan；本修正取代其中“固定标签应替换为中文标题”的错误要求。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
