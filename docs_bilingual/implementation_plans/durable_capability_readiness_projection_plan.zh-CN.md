---
doc_id: durable_capability_readiness_projection_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/durable_capability_readiness_projection_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 3
batch: 2
confirmation_required: true
---

# Durable 能力 Ready 状态投影方案

> **给 agentic workers：** 使用 `superpowers:executing-plans`。本方案只定义 installed、enabled、selected、ready 的投影与刷新，不直接安装 runtime。

## 目标

把 durable lane 的状态明确投影为 `installed`、`enabled`、`selected` 与 `ready`，禁止把这些状态折叠成一个粗略 availability flag。

## 来源方案

- codex_user_level_cross_session_durable_state_isolation_plan；automatic_orchestration_routing_enforcement_plan
- 关联治理文档：`docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md`

## 范围决策

- `installed` 表示 runtime 或 helper 可被发现。
- `enabled` 表示 capability switch 允许使用。
- `selected` 表示当前 task flow 或 selector 选择该 lane。
- `ready` 表示 preflight、receipt、selector 与 smoke/adoption gate 均满足。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local；已有 readiness checker 能检查能力链与状态词边界。
Current gate：保持 local checks、OpenSpec guard 与 local-main-first 集成；remote publication 关闭。
Runtime boundary：当前只做静态/fixture readiness 检查，不探测真实安装产物、不刷新 active selector，也不执行 smoke。
Runtime gap：若要真实反映能力状态，需要 runtime probe/refresh helper 读取 installed/enabled/selected/ready 的实际证据，并写入 repo-local readiness projection receipt。
<!-- CURRENT_STATUS_END -->

## 文件归属

- `tools/check_capability_switch_chain.py` - 校验 capability switch 依赖链与禁用/启用边界。
- `tools/check_effective_lane_fit_evidence.py` - 校验 native_omx 与 LangGraph lane fit 证据。
- `docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md` - 说明用户级 LangGraph runtime 安装与 readiness 边界。
- `test/*capability*readiness*` - 覆盖 capability readiness 投影与状态刷新行为。
- 后续 `.omx/state/*readiness*` fixture 或 receipt schema

## 热点串行规则

capability switch chain、selector schema、readiness projection schema 与 CI guard 注册必须串行。

## 并行会话契约

一个 session 独占本 implementation_plan。其他 session 可做 selector 或 receipt runtime，但 readiness projection schema 的变更必须在本方案下串行合入。

## 任务清单

## Real Runtime Implementation Gap（真实 runtime 缺口）

现有 checker 只能证明规则存在，不能证明 runtime 真实 ready。后续 runtime 包需要：

<!-- TASK_BACKLOG_START -->
- [x] Stage B：定义 installed/enabled/selected/ready 不能折叠。
- [x] Stage B：把 capability switch chain 与 lane-fit evidence 接入检查。
- [x] Stage C：记录 readiness projection 的真实 runtime gap。
<!-- TASK_BACKLOG_END -->

## Stage D pending runtime work（待实施真实 runtime）

- Stage D real runtime：实现 probe/refresh helper，读取安装 receipt、selector、smoke/adoption gate 与 backend evidence。
- Stage D real runtime：写入 readiness projection receipt，字段包含 installed、enabled、selected、ready、blockers、generated_at 与 source receipts。
- Stage D real runtime：在本地 smoke 后刷新 projection，验证 blocker 清除路径。

## 验证门禁

- `python tools/check_capability_switch_chain.py --root . --json` - 验证 capability switch 链路。
- `python tools/check_effective_lane_fit_evidence.py --root . --json` - 验证 lane-fit evidence。
- `python tools/check_precommit_update_archive.py --root . --json` - 执行提交前更新/归档检查。
- `python tools/run_openspec_guard.py --root .` - 执行 OpenSpec 与治理 guard。
- `tools/ci/local_gate.ps1` - 执行共享本地 CI gate。

## 验收标准

- 中文对照版正文为中文，保留必要 token。
- readiness 报告必须能说明每个状态的来源和 blocker。
- Stage D 前不得把静态 checker 说成真实 runtime probe。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 将 runtime probe/refresh installed/enabled/selected/ready 投影列为 Stage D pending。
- 2026-05-30 Stage B evidence：已有 capability switch chain 与 lane-fit checker 保护状态边界。
<!-- EVIDENCE_INDEX_END -->
