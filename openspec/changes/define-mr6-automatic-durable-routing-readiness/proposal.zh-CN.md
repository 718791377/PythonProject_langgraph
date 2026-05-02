## 为什么

cross-session durable-state isolation plan 现在把 MR 6 写成下一步 decision point，但仓库证据显示 automatic durable routing hookup 已经存在于更早的 team-mode surfaces 中。若不明确做 MR 6 readiness review，冷启动会话可能重复已经完成的 runtime work，或误以为现在应当立即启动 durable team。

## 变更内容

- 把 MR 6 记录为 readiness-review 与 status-reconciliation slice，而不是新的 runtime implementation slice。
- 更新双语 durable-state isolation plan，让它先指向已经实现的 automatic routing surfaces，再判断是否需要新 runtime work。
- 增加 plan-status-sync 要求：过期 rollout queue 在开启另一个 hookup implementation 前，必须先根据已有 `omx-team-auto.ps1` 证据完成 MR 6 对账。
- durable team 启动、user-level config 修改、MCP 修改和 repo-local `.omx/state/` 写入都不在本次范围内。

## 能力

### 新能力

- 无。

### 修改的能力

- `codex-user-level-team-mode-plan-status-sync`：增加 MR 6 readiness-review 覆盖，防止 rollout queue 在 existing specs、helpers 和 tests 已经提供 automatic durable routing surface 的情况下继续要求重复 hookup implementation。

## 影响

- impact_scope：`docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` 与 `.zh-CN.md` - active durable-state isolation implementation plan 对照文件。
- impact_scope：`openspec/specs/codex-user-level-team-mode-plan-status-sync/spec.md` 与 `.zh-CN.md` - stable plan-status synchronization contract。
- impact_scope：`openspec/changes/define-mr6-automatic-durable-routing-readiness/` - 本次有界 status slice 的 OpenSpec change artifacts。
- explicit_non_goals：不编辑 `C:\Users\lenovo\.codex\config.toml`，不改写 `.omx/state/`，不启动 `omx team`，不修改 MCP Router state，也不在本次 change 中重写 runtime helpers。
- rollout_sequence：创建 readiness change，更新 plan/status contract，运行 OpenSpec 与仓库 guard 验证，然后按 GitLab-first workflow 发布。
- rollback_plan：回滚本次文档与 spec-status commit；因为本次不改 runtime state 或 user-level config，所以不需要状态回滚。
- validation_path：`openspec validate --all`、`python tools/run_openspec_guard.py --root . --json`、`python tools/check_implementation_plan_rules.py --root . --json`、`python tools/check_name_clarity_rules.py --root . --json` 和 `git diff --check`。
- mainline_classification：既有 user-level Codex orchestration / cross-session durable-state isolation mainline。
