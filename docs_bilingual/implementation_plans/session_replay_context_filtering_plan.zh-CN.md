---
doc_id: session_replay_context_filtering_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/session_replay_context_filtering_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 2
batch: 2
confirmation_required: true
---

# Session Replay Context Filtering Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Filter resumed session context so stale canary text, mojibake, and legacy runtime assumptions do not re-enter prompts as current authority.

## 来源方案

- codex_user_level_context_retention_canary_plan; automatic_orchestration_routing_enforcement_plan

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
阶段：Phase 2 状态对账已收口；session replay context-filtering 包已合入本地 `main`。
责任会话：reconcile-context-retention-canary-status-20260602（仅状态对账）
当前门禁：本子方案已无剩余本地实现门禁；除非用户明确要求，否则远端发布仍未授权。
证据：本地 `main` 包含 `cbc73c7`，focused replay-filtering 覆盖仍在本地 CI manifest 中登记。
最后更新：2026-06-02
<!-- CURRENT_STATUS_END -->

## Confirmed Follow-up: Canonical Visible Canary Restore

The `prompt_canary_canonical_visible_marker_restore_plan` extends this implemented-local replay filtering baseline. The follow-up must block restored canonical marker copies in model-readable session, replay, compaction, and handoff context, while preserving user-visible transcript semantics and deriving marker values by codepoint or variable surfaces.

## 文件归属

- tools/*session*replay*
- tools/check_context_retention_canary_surface.py
- docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md
- test/*session_replay*

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- startup instruction rendering
- legacy-session compatibility wording

## 并行会话契约

- 本阶段最大并行 session 数：2。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Define replay filtering inputs and outputs for resumed legacy sessions.
- [x] Add tests for stale canary, mojibake, and stale MCP assumptions.
- [x] Implement or update filtering helper/checker boundaries.
- [x] Run context canary, mojibake, and local gate checks.
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
- 2026-05-30 Stage C implementation: added `tools/session_replay_context_filtering.py`, replay-filtering tests, CI manifest registration, and governance contract text; local validation evidence is kept in command output and git history.
- 2026-05-30 Local validation: `tools/session_replay_context_filtering.py`, context-retention canary, startup mojibake, replay-filtering tests, and `tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` passed before commit.
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-06-02 状态对账：本地 `main` ancestry 确认包含 `cbc73c7`；`test/check_session_replay_context_filtering.test.py` 存在并已在 CI manifest 登记；旧 local-main-in-progress 门禁文本已替换为 implemented-local 状态。
- 2026-06-02 canonical visible canary restore follow-up: this implemented-local replay-filtering child plan is extended by `prompt_canary_canonical_visible_marker_restore_plan` to block restored canonical marker copies in model-readable session, replay, compaction, and handoff context.
<!-- EVIDENCE_INDEX_END -->
