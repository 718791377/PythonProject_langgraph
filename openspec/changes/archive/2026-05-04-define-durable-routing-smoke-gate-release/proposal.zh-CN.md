## Why（为什么）

当前 active rollout 已经完成 durable-state MR 1 到 MR 6 的有界队列，但下一次 live routing exercise 仍需要先定义一个更小的发布边界，不能直接跳到最终 production durable-team draft。定义 Release 0.6 durable routing smoke gate 可以防止模型把“验证路由是否会选择某个 durable lane”误执行成“直接启动 durable team”。

## What Changes（变更内容）

- 在 active team-mode 与 durable-state 方案中加入 Release 0.6 durable routing smoke/adoption gate。
- 要求未来每个 smoke 或 adoption-gate change 必须声明 `target_repository` —— 当前 OpenSpec、源码和 repo-local durable state 所属的仓库根目录。
- 要求未来每个 smoke 或 adoption-gate change 必须声明 `phase` —— 当前任务阶段，例如 read-context、verify-accept、execute-parallel、integrate-converge 或 stabilize，用来驱动路由阈值。
- 要求未来每个 smoke 或 adoption-gate change 必须声明 `task` —— 这次要验证的具体任务或问题。
- 要求未来每个 smoke 或 adoption-gate change 必须声明 `operator_consent_boundary` —— 操作员授权边界，用来区分只读规划与 `-Apply`、`.omx/state/` 写入或 durable-team 启动等变更动作。
- 在最终个人生产级 durable-team draft 中加入 Release / MVP 分层说明，但不把该 draft 标成 active implementation。

impact_scope（影响范围）：只影响文档、OpenSpec requirement 和 implementation-plan sequencing。

explicit_non_goals（明确非目标）：

- 不运行 `omx-team-auto.ps1 -Apply`；`-Apply` 是让 helper 执行计划中 durable action 的开关。
- 不启动 `omx team`；`omx team` 是 durable worker-team runtime 命令。
- 不写入 `.omx/state/`；`.omx/state/` 是仓库本地 durable-state 目录。
- 不编辑 `C:\Users\lenovo\.codex\config.toml`；该文件是用户级 Codex 配置文件。
- 不修改 MCP Router state；MCP Router 是共享 MCP 管理层，不管理 Codex 专用的 `omx_*` MCP 工具。

rollout_sequence（发布顺序）：

1. 在 active implementation plans 中定义 Release 0.6 gate。
2. 为四个必填 gate 字段增加 OpenSpec requirement。
3. 最终 production plan 只增加 release-train overlay，继续保持 draft。
4. 运行 OpenSpec 与仓库文档 checkers。
5. 走 GitLab-first review，再同步 GitHub mirror。

rollback_plan（回滚方案）：回滚本次文档和 spec 变更；本次不修改 runtime state 或用户级配置。

validation_path（验证路径）：

- `openspec validate --all` —— 验证 OpenSpec specs 和 active / archived changes。
- `python tools/run_openspec_guard.py --root . --tool codex --json` —— 运行仓库 OpenSpec aggregate guard。
- `python tools/check_name_clarity_rules.py --root . --json` —— 检查脚本、路径、命令、变量和 profile 名称后是否有简短解释。
- `python tools/check_implementation_plan_rules.py --root . --json` —— 检查 implementation-plan registry 规则。
- `git diff --check` —— 检查 whitespace 和 patch hygiene。

mainline_classification（主线分类）：属于现有 active Codex user-level team-mode 与 cross-session durable-state rollout line；不是新主线，也不是直接实施 production durable-team draft。

## Capabilities（能力）

### New Capabilities（新增能力）

- 无。

### Modified Capabilities（修改能力）

- `codex-user-level-team-mode-automatic-team-routing`：定义 smoke/adoption-gate 的必填字段和只读默认边界，作为未来 live routing exercise 的前置条件。

## Impact（影响）

- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` —— active 英文 team-mode implementation plan。
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` —— active 中文 team-mode implementation plan 对照版。
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` —— active 英文 durable-state isolation plan。
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md` —— active 中文 durable-state isolation plan 对照版。
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` —— draft 英文北极星方案。
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` —— draft 中文北极星方案对照版。
- `openspec/specs/codex-user-level-team-mode-automatic-team-routing/spec.md` —— stable automatic routing capability，归档时会接收本次 delta requirement。
