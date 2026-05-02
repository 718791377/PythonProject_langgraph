## 为什么

cross-session durable-state isolation plan 仍然把 MR 5 写成下一步 active implementation slice，但 helper mirror source-of-truth slice 已经落地、通过验证并归档。冷启动会话如果继续读取旧表述，可能会重复已经完成的工作，或选错下一步。

## 变更内容

- 在双语 cross-session durable-state isolation plan 中把 MR 5 标记为已完成。
- 引用已经落地的 helper mirror source-of-truth 证据和已归档 OpenSpec change。
- 将下一步重述为 MR 6 readiness review 或 automatic durable routing hookup，而不是再次实施 MR 5。
- 增加 plan-status-sync 要求，防止已经完成的 durable-state rollout slice 继续被标成下一步 active slice。

## 能力

### 修改的能力
- `codex-user-level-team-mode-plan-status-sync`：扩展状态同步要求，覆盖 cross-session durable-state rollout queue。

## 影响

- 影响范围：`docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` - 英文 ASCII implementation plan 主文。
- 影响范围：`docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md` - UTF-8 中文 companion plan。
- 影响范围：`openspec/specs/codex-user-level-team-mode-plan-status-sync/spec.md` 与 `.zh-CN.md` - plan status sync 的稳定规范。
- 非目标：不修改 `C:\Users\lenovo\.codex\config.toml`，不修改 `.omx/state/`，不启动 durable team，也不在此 change 内实施 MR 6。
- 验收：OpenSpec 验证、guard、name-clarity 检查、implementation plan 检查和 diff whitespace 检查通过。
