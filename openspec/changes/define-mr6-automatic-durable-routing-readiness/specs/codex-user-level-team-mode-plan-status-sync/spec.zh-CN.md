## ADDED Requirements / 新增要求

### Requirement: MR 6 readiness review SHALL reconcile automatic routing evidence before opening duplicate runtime hookup work / MR 6 readiness review 必须先对账 automatic routing 证据，再开启重复 runtime hookup work
当 durable-state rollout queue 把 MR 6 写成下一步 automatic durable routing hookup 时，plan-status sync process 必须先检查仓库是否已经包含满足该 hookup 的 stable automatic routing specs、generated helper source 和 tests。如果证据存在，queue 必须把 MR 6 readiness review 标记为完成，并把未来 runtime exercise 放进单独显式的 smoke 或 adoption-gate slice。

#### Scenario: Automatic routing evidence already exists / automatic routing 证据已经存在
- **WHEN** `codex-user-level-team-mode-automatic-team-routing` 已经规范了 `omx-team-auto.ps1` 的行为
- **AND** 仓库测试已经覆盖 effective lane selection、selector safety、empty residue handling、native_omx lifecycle actions 和 LangGraph graph-signal selection
- **THEN** durable-state rollout plan 不得继续把 MR 6 标记为尚未实现的 automatic durable routing hookup
- **AND** 它必须把冷启动会话指向未来显式 live smoke 或 adoption-gate step，而不是重复 runtime implementation
