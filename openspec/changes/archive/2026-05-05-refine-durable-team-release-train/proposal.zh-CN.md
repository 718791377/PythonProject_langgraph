## Why / 为什么

当前 active plans 已经把 `R0.6 Durable Routing Smoke Gate` 写成下一条 release slice，但从 R0.6 到 `R2.0 Production Durable Team` 的路径仍然太粗。未来冷启动会话需要更细的 release train，避免从只读 smoke gate 直接跳到 draft production target。

## What Changes / 变更内容

- 细化 active team-mode plan，把 R0.6.0 到 R2.0.8 的小版本切片写清楚。
- 细化 active durable-state isolation plan，明确下一步先做 R0.6.0 与 R0.6.1，再进入状态采样或 dry-run routing。
- 细化 draft personal production durable-team plan 的 MVP / release ladder，同时保持该计划 `status: draft`。
- 新增 OpenSpec 要求：roadmap slices 必须独立 review、可回滚，并且有 operator consent boundary。

impact_scope: 只影响文档、OpenSpec requirements 和 implementation-plan sequencing。

explicit_non_goals:

- 不运行 `omx-team-auto.ps1 -Apply`；`-Apply` 是执行 planned durable action 的 helper 开关。
- 不启动 `omx team`；`omx team` 是 durable worker-team runtime 命令。
- 不写 `.omx/state/`；`.omx/state/` 是 repo-local durable-state 目录。
- 不提升 `codex_cli_personal_production_durable_team_plan.md`；该文件仍然是英文 draft north-star plan。
- 不修改 `C:\Users\lenovo\.codex\config.toml`；该文件是用户级 Codex 配置文件。

rollout_sequence:

1. 更新 active team-mode release overlay。
2. 更新 active durable-state next-decision section。
3. 更新 draft production durable-team release ladder。
4. 增加 OpenSpec release-slice requirement。
5. 运行 OpenSpec 和仓库文档 checker 验证。

rollback_plan: 回滚本次文档和 spec 变更；不涉及 runtime state 或用户级配置变更。

validation_path:

- `openspec validate --all` - 验证 OpenSpec specs 以及 active / archived changes。
- `python tools/run_openspec_guard.py --root . --tool codex --json` - 运行聚合 OpenSpec 仓库 guard。
- `python tools/check_name_clarity_rules.py --root . --json` - 检查脚本、路径、命令、变量、profile、角色名等是否带有简短解释。
- `python tools/check_implementation_plan_rules.py --root . --json` - 验证 implementation-plan registry 规则。
- `git diff --check` - 检查空白字符和 patch hygiene。

mainline_classification: 这是现有 active Codex user-level team-mode 与 durable-state implementation line 的 roadmap refinement；不是 runtime implementation，也不是启用 production draft。

## Capabilities / 能力影响

### New Capabilities / 新能力

- 无。

### Modified Capabilities / 修改能力

- `codex-user-level-team-mode-plan-status-sync`：要求 release-train roadmap slices 在 R2.0 production claims 之前保持小步、独立 review、可回滚，并受 operator consent boundary 约束。

## Impact / 影响文件

- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - active 英文 team-mode implementation plan。
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` - active 中文 team-mode implementation plan 对照版。
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` - active 英文 durable-state isolation plan。
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md` - active 中文 durable-state isolation plan 对照版。
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` - draft 英文 north-star plan。
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` - draft 中文 north-star plan 对照版。
- `openspec/specs/codex-user-level-team-mode-plan-status-sync/spec.md` - archive 时接收 delta 的 stable plan-status capability。
