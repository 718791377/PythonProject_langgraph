---
doc_id: durable_smoke_adoption_gate_template_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/durable_smoke_adoption_gate_template_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 3
batch: 2
confirmation_required: true
---

# Durable Smoke 与 Adoption Gate 模板方案

> **给 agentic workers：** 使用 `superpowers:executing-plans`。本方案先定义 smoke/adoption gate 模板；真实 live adoption 必须另有 runtime evidence。

## 目标

在允许任何 live durable runtime exercise 或 apply-mode adoption 之前，建立 durable smoke 与 adoption gate template。

## 来源方案

- codex_user_level_cross_session_durable_state_isolation_plan
- 关联命令：`codex-durable-state-status.ps1`、`tools/install-codex-user-level-team-mode.ps1`

## 范围决策

- 模板默认 read-only，不执行 live adoption。
- smoke 必须先产生 bounded transcript、timeout release 与 rollback readiness。
- apply-mode adoption 必须有 operator authorization 与 selector/readiness evidence。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local；smoke/adoption gate template 和自检 fixture 已存在。
Current gate：本地检查、OpenSpec guard 与 local-main-first 集成；remote publication 关闭。
Runtime boundary：当前模板不会启动真实 durable runtime，不执行 apply-mode adoption，也不会选择 live backend。
Runtime gap：真实 durable smoke、apply-mode adoption 或 live adoption 执行层仍需 runtime helper，写入 smoke-tested receipt、adoption decision、selected backend、rollback pointer、selector state 与 timeout release evidence。
<!-- CURRENT_STATUS_END -->

## 文件归属

- durable smoke/adoption gate template fixture
- `tools/check_durable_smoke_adoption_gate_template.py` - 校验 durable smoke/adoption gate template 与 fixture。
- `codex-durable-state-status.ps1` - 读取跨 backend durable-state 摘要。
- 后续 smoke/adoption runtime receipt schema

## 热点串行规则

smoke/adoption template、selector ownership、readiness projection 与 backend selection schema 是共享热点，必须串行修改。

## 并行会话契约

一个 session 独占本 implementation_plan。其他 runtime lane 可并行准备 install/smoke helper，但不得绕过本 gate 直接声明 live adoption。

## 任务清单

## Real Runtime Implementation Gap（真实 runtime 缺口）

现有模板和 fixture 只能证明规则，不代表真实 durable runtime 已执行。

<!-- TASK_BACKLOG_START -->
- [x] Stage B：建立 durable smoke/adoption gate template。
- [x] Stage B：添加自检 fixture，包含 negative adoption-gate fixture。
- [x] Stage C：记录真实 durable smoke/adoption runtime 仍是 pending。
<!-- TASK_BACKLOG_END -->

## Stage D pending runtime work（待实施真实 runtime）

- Stage D real runtime：实现真实 durable smoke helper，写入 `smoke-tested` receipt。
- Stage D real runtime：实现 apply-mode adoption helper，读取 selector/readiness/receipt 后写入 adoption decision。
- Stage D real runtime：为 live adoption 写入 selected backend、rollback pointer、timeout release、cleanup evidence 与 remote publication closed 记录。

## 验证门禁

- `python tools/check_durable_smoke_adoption_gate_template.py --root . --json` - 验证 smoke/adoption gate template。
- `python tools/check_durable_artifact_state_surfaces.py --root . --json` - 验证 durable artifact/state surfaces。
- `python tools/check_precommit_update_archive.py --root . --json` - 执行提交前更新/归档检查。
- `python tools/run_openspec_guard.py --root .` - 执行 OpenSpec 与治理 guard。
- `tools/ci/local_gate.ps1` - 执行共享本地 CI gate。

## 验收标准

- 中文对照版正文为中文。
- 模板和 runtime helper 区分明确。
- Stage D 前不得声明真实 durable smoke 或 adoption 已完成。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 将真实 durable smoke、apply-mode adoption 与 live adoption helper 标记为 Stage D pending。
- 2026-05-30 Stage B evidence：durable smoke/adoption gate template 与 fixture 已通过本地 checker。
<!-- EVIDENCE_INDEX_END -->
