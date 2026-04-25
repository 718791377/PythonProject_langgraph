---
doc_id: project_startup_summary
lang: zh-CN
status: active
doc_class: startup_summary
translation_of: docs_bilingual/project_startup_summary.md
---

# 项目启动摘要

## 目标

本仓库是 Codex 用户级编排主线的主仓库，范围包括：

- 原生 Codex subagents
- oh-my-codex 用户级工作流表面
- OMX durable-team 编排
- LangGraph durable orchestration

本仓库对 LangGraph 采用三层口径：用户级共享层提供跨项目复用的官方 runtime 与 tooling，本仓库是项目级承接层，负责 repo-local 的兼容或编排源码与 startup-facing policy，而 repo-local durable truth 固定落在 `.omx/state/langgraph/`。任何生成到用户级目录的 helper 副本都只是安装产物，不是 source of truth。

## 当前仓库姿态

稳定的仓库级入口状态：

- 基础层完成
- 本仓库仍然是用户级 Codex 编排产品线的主仓库
- 当前命名中的仓库主线是 `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`

稳定的能力状态：

- `subagent`
  - 已经达到 leader 层个人生产可用
- `native_omx`
  - 已经达到原生 Windows 上 worker-centric durable lane 的个人生产可用
- `langgraph`
  - 已经是真实可用的 additive durable backend
  - 但仍然属于“可用但偏 MVP”，还不是 fully realized 的 LangGraph-native runtime

## 当前实施边界

当前实施主线只限于两份 active 用户级编排方案：

- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md`：当前正在实施的用户级团队模式方案，用来约束 native Codex、oh-my-codex、native_omx 与 LangGraph 的路由行为。
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md`：当前正在实施的 durable state 隔离方案，用来防止 repo-local state 跨项目或跨会话误泄漏。

长期最终目标仍然只是 draft：

- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md`：个人开发者生产级持久化 Codex CLI 团队的最终目标草案；不要把它当成已经实现的运行时能力。

跨项目使用规则：

- `D:\PythonProject_OpenClaw`：消费者项目，可以复用用户级 Codex 编排 policy 和浏览器自动化能力，但必须保留自己的 repo-local facts 与 `.omx/state/`。
- `D:\PythonProject_CLIProxyAPI`：消费者项目，可能需要浏览器或 endpoint 验证，但必须保留自己的 repo-local facts 与 `.omx/state/`。
- `D:\project`：通用项目根目录，默认先按 core profile 处理，只有项目证据需要时才增加 browser、web 或 orchestration 能力。
- 后续新项目：只能消费共享的用户级 runtime 与 policy；每个项目仍然拥有自己的 OpenSpec artifacts、durable state、CI 状态和发布状态。

不要在 startup 或边界冻结工作中自动启动 durable team。只有在计划已经冻结且存在至少两个基本独立的执行切片时，才允许启动 durable team。

当前 no-touch durable-state baseline：

- `docs_bilingual/memory/cross_project_durable_state_read_only_inventory_2026-04-25.zh-CN.md`：面向 `D:\PythonProject_langgraph`、`D:\PythonProject_OpenClaw`、`D:\PythonProject_CLIProxyAPI` 与 `D:\project` 的只读 Phase 0 盘点；它只能作为实施证据，不能当成允许修改 `.omx/state` 的授权。

易漂移的执行细节已经下放到主线 memory 摘要，而不再放在这份仓库级入口摘要里。

## 冷启动阅读顺序

1. 本文
2. `docs_bilingual/project_startup_summary.md`
3. `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md`
4. `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md`
5. `AGENTS.md`
6. `docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md`
7. `docs_bilingual/governance/user_level_launcher_payload_policy.zh-CN.md`
8. `docs_bilingual/governance/openspec_usage_convention.zh-CN.md`
9. `docs_bilingual/governance/openspec_opsx_project_usage_policy.zh-CN.md`
10. `docs_bilingual/governance/openspec_official_workflow_policy.zh-CN.md`
11. `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md`
12. `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md`
13. 当前正在实现的 active OpenSpec change

## 当前主线

- `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`

## 当前活动细节位置

如果需要读取易漂移的执行细节，请转到：

- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md`
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md`

那份主线 memory 摘要承载：

- 当前维护支线
- 最近会话带来的 operator workflow（操作员工作流） 变化
- 已冻结的下一轮 change 简报
- 当前 change readiness（变更就绪性） 结论

更详细的 LangGraph 后续 change 队列，应阅读：

- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md`
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md`

这类详细队列应放在 implementation plan 层，而不是放大到 startup summary。

## 边界

本仓库负责 Codex 用户级编排产品线。

对 LangGraph 而言，本仓库拥有 repo-local 兼容层源码与 repo-local durable-state contract。官方上游包应安装在用户级共享 LangGraph venv 中，而不是安装到本仓库目录里。

对用户级 launcher 行为而言，本仓库也拥有防止 Windows 启动命令行超长的 startup payload policy。

本仓库不负责：

- OpenClaw 应用运行时工作
- OpenClaw 服务编排
- OpenClaw 仓库内部的 WeCom 与 local-control 主线

## 防跑偏规则

- 这条编排主线今后只在本仓库继续推进
- 不要再回到 `D:\PythonProject_OpenClaw` 为这条线继续做新实现
- OpenSpec 历史必须和代码一起迁移
- 在开始新的大实施批次前，先更新 startup summary 与当前主线状态

## 仓库发布流程

- GitLab 是本仓库的权威 review / merge 面。
- 所有变更先推送到 GitLab feature 分支并创建或更新 GitLab MR；只有 GitLab pipeline 通过后，才合并到 GitLab `main`。
- GitLab `main` 合并并变绿后，再把同一个 `main` 提交直接同步推送到 GitHub。
- 默认不为 GitHub 开 PR；除非用户明确要求，GitHub 只是合并后的同步目标。
