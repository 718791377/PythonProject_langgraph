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
