---
doc_id: repo_local_selector_ownership_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/repo_local_selector_ownership_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 3
batch: 2
confirmation_required: true
---

# Repo-local Selector Ownership 方案

> **给 agentic workers：** 使用 `superpowers:executing-plans`。本方案只管理 repo-local active selector 的所有权边界。

## 目标

确保 active durable selector 是 repository-local 的，不能跨 repository 或 worktree 泄漏，也不能从兼容性记录中被自动采用。

## 来源方案

- codex_user_level_cross_session_durable_state_isolation_plan
- 相关状态路径：`.omx/state/selectors/active.json`

## 范围决策

- selector 必须写入当前 repo-local `.omx/state/selectors/active.json`。
- 没有 active selector 时，自动 durable adoption 必须报告 selector refresh gap。
- compatibility records 只能作为 inspectable evidence，不得自动接管。
- selector lease 必须能释放或过期。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local；selector ownership checker/guard 已存在，能够阻止跨 repo selector 泄漏和 compatibility-record auto-adopt。
Current gate：本地检查、OpenSpec guard 与 local-main-first 集成；remote publication 关闭。
Runtime boundary：当前 checker 不会自动写入、续租或释放 active selector。
Runtime gap：若要自动选择/刷新 active selector，需要 runtime helper 写入/续租/释放 selector，并记录 owner_session、backend_family、lease_expires_at、refresh reason 与 rollback/cleanup evidence。
<!-- CURRENT_STATUS_END -->

## 文件归属

- `.omx/state/selectors/active.json` schema 或 fixture
- `tools/check_durable_artifact_state_surfaces.py` - 校验 selector adoption 与 durable artifact/state surface。
- `tools/check_repo_local_selector_ownership.py` 或相关 checker
- `test/*selector*ownership*` - 覆盖 repo-local selector ownership 与 lease/refresh 行为。

## 热点串行规则

active selector schema、backend selection record、durable adoption gate 与 readiness projection 互为热点，必须串行修改 schema。

## 并行会话契约

一个 session 独占本 implementation_plan。其他 session 可并行实现 readiness 或 receipt helper，但只能读取 selector 输出，不能同时改 selector schema。

## 任务清单

## Real Runtime Implementation Gap（真实 runtime 缺口）

现有能力是 checker/guard，不是 selector runtime。后续 runtime 包需要：

<!-- TASK_BACKLOG_START -->
- [x] Stage B：定义 repo-local active selector ownership 规则。
- [x] Stage B：阻止 compatibility records 被自动采用。
- [x] Stage C：记录 selector runtime helper 缺口。
<!-- TASK_BACKLOG_END -->

## Stage D pending runtime work（待实施真实 runtime）

- Stage D real runtime：实现 active selector 写入、续租、释放 helper。
- Stage D real runtime：写入 owner_session、backend_family、selected_reason、lease_expires_at、created_at、updated_at 与 rollback/cleanup evidence。
- Stage D real runtime：在 selector 不存在或过期时刷新 readiness blocker。

## 验证门禁

- `python tools/check_durable_artifact_state_surfaces.py --root . --json` - 验证 selector durable-state surfaces。
- `python tools/check_orchestration_collaboration_evidenceguard.py --root . --json` - 验证协同证据 guard。
- `python tools/check_precommit_update_archive.py --root . --json` - 执行提交前更新/归档检查。
- `python tools/run_openspec_guard.py --root .` - 执行 OpenSpec 与治理 guard。
- `tools/ci/local_gate.ps1` - 执行共享本地 CI gate。

## 验收标准

- 中文对照版正文为中文。
- selector helper 不得跨 repo 写入。
- Stage D 前不得声明 selector 自动刷新已实现。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 将 active selector 写入/续租/释放 helper 列为 Stage D pending。
- 2026-05-30 Stage B evidence：已有 selector ownership checker 约束 repo-local selector 边界。
<!-- EVIDENCE_INDEX_END -->
