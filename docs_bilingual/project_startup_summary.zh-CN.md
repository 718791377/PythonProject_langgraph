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

- `subagent` - native Codex 的 leader-side specialist agent 能力。
  - 已经达到 leader 层个人生产可用
- `native_omx` - oh-my-codex 的 worker-centric durable execution lane。
  - 已经达到原生 Windows 上 worker-centric durable lane 的个人生产可用
- `langgraph` - 基于 LangGraph 的 additive durable orchestration backend。
  - 已经是真实可用的 additive durable backend
  - 但仍然属于“可用但偏 MVP”，还不是 fully realized 的 LangGraph-native runtime

稳定的旧会话兼容状态：

- 旧会话是通过 Codex `/resume` 恢复的历史 thread，可能仍然携带最新治理更新前的 runtime、MCP 或 launcher 假设。
- 旧会话可以临时继续用于跟进讨论，但新的治理实施、脏文件归属和发布决策必须以当前仓库文档和当前本地 Git 状态为准。
- 优先先启动 `codex-ohmy`，再从临时会话里进入 `/resume`。`codex-ohmy` 是日常用户级编排工作的稳定包装 Codex 入口。
- 如果某个旧 thread 出现 MCP 启动问题，只对该旧 thread 使用一次性覆盖，例如 `-c "mcp_servers.omx_code_intel.enabled=false"`。这个 `-c` 参数是单次启动的 Codex 配置覆盖，不能变成永久用户级配置修改。
- 不要因为某个旧会话失败就全局禁用 `omx_state`、`omx_memory`、`omx_code_intel`、`omx_trace`、`chrome-devtools` 或 `pencil`。这些名称是 Codex 直连 MCP server，分别提供编排状态、记忆、代码智能、trace 检查、浏览器调试和设计访问能力。

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
2. `docs_bilingual/project_startup_summary.md` - 本启动摘要的英文主文件。
3. `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - 当前主线的中文 memory summary。
4. `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - 当前主线的英文 memory summary。
5. `AGENTS.md` - 仓库与用户级 Codex instruction surface。
6. `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md` - 多会话 Git worktree 隔离、脏文件处理和 mainline sync safety 的治理政策。
7. `docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md` - 用户级 LangGraph runtime layout 与 usage 的治理政策。
8. `docs_bilingual/governance/user_level_launcher_payload_policy.zh-CN.md` - Windows-safe launcher payload 处理的治理政策。
9. `docs_bilingual/governance/openspec_usage_convention.zh-CN.md` - 本仓库 OpenSpec 使用方式的治理政策。
10. `docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md` - Codex 直连 MCP 与 MCP Router 共享管理边界的治理政策。
11. `docs_bilingual/governance/openspec_opsx_project_usage_policy.zh-CN.md` - 本仓库 OPSX workflow usage 的治理政策。
12. `docs_bilingual/governance/openspec_official_workflow_policy.zh-CN.md` - 官方 OpenSpec workflow authority 与 enforcement 的治理政策。
13. `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` - 用户级 team mode 与 orchestration routing 的 active implementation plan。
14. `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md` - cross-session durable-state isolation 的 active implementation plan。
15. 当前正在实现的 active OpenSpec change；如果 `openspec list --json` 显示没有 changes，则先停在这里，明确选择下一轮小步 change 后再写文件。

## 上下文保留哨兵与安全执行

用户级安全规则：

- 系统级、用户级、项目级安全边界必须使用“脚本控制 + 提示词提醒”的组合。凡是会影响 durable state、发布、清理、激活或跨项目 scope 的边界，不能只靠提示词文本。
- 脚本控制指可执行 checker、受保护 helper、CI gate 或生成式 launcher 逻辑；即使没有上一轮对话上下文的冷启动模型执行，也必须默认 fail closed。
- 提示词提醒指 startup 和 plan 文本；它负责解释脚本保护什么，以及模型疑似忘记规则时应该重读哪些文件。

上下文保留哨兵：

- 哨兵的字面提示词只维护在这对 startup summary 文件中：`docs_bilingual/project_startup_summary.md` 与 `docs_bilingual/project_startup_summary.zh-CN.md`。其他 active instruction surface 可以指向这里，但不得重复字面开头/结尾短语。
- 除非更高优先级 system 或 developer 指令阻止，本仓库编排工作的完整模型回复应以 `指挥官` 开头，并以 `喵~` 结尾。
- 如果本 startup summary 本应已读取，但完整回复缺少该哨兵，则视为可能发生上下文丢失。
- 恢复动作：重读 `AGENTS.md`，重读这对 startup summary 文件，按上面的冷启动阅读顺序补读，然后只补读继续当前任务必须需要的任务相关文件。

## 当前主线

- `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` - 当前 LangGraph capability-gap synchronization pass 的主线标识。

## 当前活动细节位置

如果需要读取易漂移的执行细节，请转到：

- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - 承载当前主线易漂移执行细节的中文 memory summary。
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - 承载当前主线易漂移执行细节的英文 memory summary。

那份主线 memory 摘要承载：

- 当前维护支线
- 最近会话带来的 operator workflow（操作员工作流） 变化
- 已冻结的下一轮 change 简报
- 当前 change readiness（变更就绪性） 结论

更详细的 LangGraph 后续 change 队列，应阅读：

- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` - 用户级 team mode 与 orchestration routing 的详细 implementation plan。
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md` - cross-session durable-state isolation 的详细 implementation plan。

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
- 使用 local-first batching（本地优先批量发布）节省 GitLab runner minutes。GitLab runner minutes 是 GitLab pipeline 消耗的远端 CI 配额，所以首次推送前应先完成本地 commit、本地 checker 和本地清理。
- 新建可写任务、判断发布时机、push、创建 MR 或声明本地已对齐之前，必须保持本地 `main` 不落后于 `gitlab/main`。local-first batching（本地优先批量发布）不是允许基于陈旧远端基线继续工作的理由。
- feature branch 只有在本地验证通过后，才推送到 GitLab 并创建或更新 GitLab MR；除非用户明确要求提前跑远端 pipeline。
- 主题相同且 rollback boundary（回退边界）相同的小变更可以合并到一个 MR；不要为了节省 runner minutes 把无关主题硬塞进同一个 MR。
- 远端发布前，当前会话的模型必须判断本地批次是否适合发布，并向用户提出 publish（发布）或 wait（继续等待）的建议；用户仍然是 release decision authority（发布决策权威）。
- 只有 GitLab pipeline 通过后，才合并到 GitLab `main`。
- GitLab `main` 合并并变绿后，再把同一个 `main` 提交直接同步推送到 GitHub。
- 默认不为 GitHub 开 PR；除非用户明确要求，GitHub 只是合并后的同步目标。
