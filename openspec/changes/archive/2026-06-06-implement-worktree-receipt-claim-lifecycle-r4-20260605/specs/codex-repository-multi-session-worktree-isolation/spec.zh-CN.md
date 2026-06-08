## MODIFIED Requirements

### Requirement: Feature worktrees SHALL carry task receipts and lifecycle metadata

仓库必须要求每个新建 feature worktree（功能工作树）在可写工作开始前携带 task receipt metadata（任务收据元数据）。

metadata（元数据）必须存在于两个 local-only surfaces（仅本地表面）：

- `.omx/session-claims/<session>.json` - 用于 session ownership（会话所有权）和 conflict checks（冲突检查）。
- worktree 内部的 `.omx/worktree-task-receipt.json` - 用于 resumed-session task identification（恢复会话的任务识别）。

两个表面都必须至少记录 worktree path、branch、creating or taking-over session、task name、task summary、document-plan-only flag、later-code-required flag、touched paths、next action、local-main merge requirement、remote-sync requirement、expected merge-or-pause point，以及 lifecycle status。

Allowed lifecycle statuses（允许生命周期状态）必须包含 `active`、`paused`、`ready-to-merge`、`merged-local-main`、`cleaned`、`remote-sync-needed`、`completed`、`superseded` 和 `stale`。`stale` 与 `superseded` 用来分类 residual or obsolete work（残留或过时工作），但不声明 local-main integration、cleanup、branch deletion 或 remote publication 已完成。`merged-local-main`、`cleaned`、`remote-sync-needed` 和 `completed` worktree 必须携带 completion receipt fields（完成收据字段），包括 rollback ref、local-main commit、cleaned worktree path、deleted branch 和 remote sync status。

每次 runtime lifecycle transition（运行时生命周期转换）都必须追加 transition-ledger entry（转换账本条目），记录 owner、previous state、next state、transition timestamp、evidence paths、适用时的 rollback ref、适用时的 local-main commit、cleanup decision、适用时的 reason，以及 remote-publication authorization status。

#### Scenario: Runtime helper advances active work to ready-to-merge

- **WHEN** lifecycle helper 将 branch-matching receipt and claim（与分支匹配的收据和认领）从 `active` 推进到 `ready-to-merge`
- **THEN** 它必须更新两个 local-only metadata surfaces
- **AND** 它必须追加带 owner、previous state、next state、timestamp、evidence paths、cleanup decision 和 remote-publication authorization status 的 transition-ledger entry
- **AND** 它不得修改 local `main` 或任何 remote ref

#### Scenario: Runtime helper records local-main merge evidence

- **WHEN** local-main flow 记录 `ready-to-merge` 到 `merged-local-main`
- **THEN** helper 必须要求 rollback ref 和 local-main commit evidence
- **AND** 它必须保持 `remote_publication_authorized=false`
- **AND** completion fields 必须满足 worktree task receipt checker

#### Scenario: Runtime helper records cleaned evidence

- **WHEN** guarded cleanup 移除已集成 worktree 并删除已合并本地 branch
- **THEN** preserved completed claim 必须记录 `lifecycle_status=cleaned`，其中 `cleaned` 表示受保护清理已移除本地 worktree、删除已合并本地 branch 并保留完成证据
- **AND** 它必须记录 removed worktree、deleted branch、rollback ref、local-main commit 和 remote sync status
- **AND** 它必须保留 cleanup evidence，且不得删除 backup refs 或 remote refs

#### Scenario: Runtime helper records exceptional lifecycle states

- **WHEN** worktree 在 local-main integration 前被暂停、取代或标记为 stale
- **THEN** helper 必须要求 reason 或 evidence path
- **AND** 它必须追加 transition-ledger entry
- **AND** 它不得要求 integration 或 cleanup states 专用的 completion fields
