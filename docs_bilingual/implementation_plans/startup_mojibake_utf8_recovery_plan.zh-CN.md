---
doc_id: startup_mojibake_utf8_recovery_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/startup_mojibake_utf8_recovery_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 2
batch: 2
confirmation_required: true
---

# Startup Mojibake UTF8 Recovery Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Detect mojibake in startup and instruction authority surfaces and recover from UTF-8 canonical files.

## 来源方案

- codex_user_level_context_retention_canary_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 2。
- 阶段：Phase 2。
- 状态：本文件是 active 子 implementation_plan，但在本地 `main` 合入后仍必须等待用户确认，才能开始非文档实现。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：implemented-local
阶段：Phase 2 状态对账已收口；startup mojibake UTF-8 recovery 包已合入本地 `main`。
责任会话：reconcile-context-retention-canary-status-20260602（仅状态对账）
当前门禁：本子方案已无剩余本地实现门禁；除非用户明确要求，否则远端发布仍未授权。
证据：本地 `main` 包含 `43d3ae9`，当前 startup mojibake checker 报告 `ok: true`。
最后更新：2026-06-02
<!-- CURRENT_STATUS_END -->

## Confirmed Follow-up: Canonical Visible Canary Restore

The `prompt_canary_canonical_visible_marker_restore_plan` reuses this implemented-local UTF-8 recovery baseline. The follow-up must treat the startup summary pair as the only canonical literal surface, derive restored marker values outside startup files, keep diagnostics from echoing marker literals, and block marker copies from model-readable session context.

## 文件归属

- tools/check_startup_instruction_mojibake.py
- docs_bilingual/project_startup_summary.md
- docs_bilingual/project_startup_summary.zh-CN.md
- test/*mojibake*

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- startup summary pair
- AGENTS.md authority surface

## 并行会话契约

- 本阶段最大并行 session 数：2。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add mojibake fixtures covering Chinese startup text and corrupted canary markers.
- [x] Extend the checker to report exact recovery sources instead of copying corrupted text.
- [x] Update governance text to treat UTF-8 files as canonical.
- [x] Run mojibake checker and local gate.
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
- 2026-05-30 Stage C 实施：checker 输出现在报告 canonical UTF-8 recovery sources，并对 mojibake findings 做去污染摘要，避免回显损坏文本；startup summary pair 已记录恢复源。
- 2026-05-30 Stage C 验证：在 `implement-startup-mojibake-utf8-recovery-20260530` 分支上，`python test/check_startup_instruction_mojibake.test.py`、`python tools/check_startup_instruction_mojibake.py --root . --json`、`python tools/check_implementation_plan_rules.py --root . --json`、`python tools/check_precommit_update_archive.py --root . --json` 和 `python tools/check_worktree_task_receipt.py --root . --json` 已通过；完整本地 CI 与本地 MR review 仍是当前集成门禁。
- 2026-05-30 Stage C 进入：用户确认继续实施本子方案；runtime/checker 工作前已创建 active session claim。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-06-02 状态对账：本地 `main` ancestry 确认包含 `43d3ae9`；`python tools/check_startup_instruction_mojibake.py --root . --json` 报告 `ok: true`；旧本地验证门文本已替换为 implemented-local 状态。
- 2026-06-02 canonical visible canary restore follow-up: this implemented-local UTF-8 recovery child plan supplies the baseline for restoring the startup-summary-defined canonical visible canary while keeping diagnostics literal-free and model-readable context filtered.
<!-- EVIDENCE_INDEX_END -->
