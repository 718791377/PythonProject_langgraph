# 设计：Worktree Receipt Claim Lifecycle R4

## Overview

新增 `tools/advance_worktree_task_lifecycle.py`，作为 receipt（任务收据）与 claim（会话认领）生命周期推进的唯一 runtime helper（运行时辅助脚本）。该 helper 在相关 local-only metadata surfaces（仅本地元数据表面）存在时同步更新：

- feature worktree（功能工作树）内部的 `.omx/worktree-task-receipt.json`。
- 同一 worktree 内 `.omx/session-claims/<session>.json` 的 branch-matching claim（与当前分支匹配的认领）。

helper 每次 state change（状态变化）都会追加 `lifecycle_transitions` ledger entry（生命周期转换账本条目）。它不会修改 remotes（远端引用），也不会自行合并 local main（本地 `main`）。

## Transition model

Allowed next states（允许的下一状态）复用现有 receipt/claim lifecycle vocabulary（收据/认领生命周期词表）：

- `active` - worktree 当前由任务 owner 拥有，允许继续写入。
- `paused` - owner 在合并前有意暂停，并留下 resume reason（恢复原因）。
- `ready-to-merge` - local validation（本地验证）已完成，package 可进入 local-main integration（本地 `main` 集成）。
- `merged-local-main` - local `main` 已包含 feature branch 结果，并且 rollback evidence（回滚证据）存在。
- `completed` - local package evidence（本地包证据）完整，但 remote publication（远端发布）仍受单独授权门约束。
- `cleaned` - guarded cleanup（受保护清理）已移除 local worktree，并删除已合并的本地 feature branch。
- `remote-sync-needed` - local completion（本地完成）后仍需要之后显式授权的 remote publication 或 mirror sync。
- `superseded` - 本 work 在 local-main integration 前已被其他 package 替代。
- `stale` - residual work（残留工作）被分类为 obsolete（过时），但不声称已合并或已清理。

helper 对 invalid order（无效顺序）采用 fail-closed（失败即关闭）策略。正常 forward transitions（正向转换）包括：

1. `active` 或 `paused` 到 `ready-to-merge`
2. `ready-to-merge` 到 `merged-local-main`
3. `merged-local-main` 或 `completed` 到 `cleaned`

来自 `active`、`paused` 或 `ready-to-merge` 的 exceptional transitions（异常转换）可在记录 reason（原因）后转为 `paused`、`superseded` 或 `stale`。

## Evidence fields

每个 transition（状态转换）记录：

- `transitioned_at` - lifecycle transition 被记录时的 timestamp（时间戳）。
- `owner` - 记录 lifecycle transition 的 helper 或 session。
- `previous_state` - transition 前的 lifecycle state。
- `next_state` - transition 后的 lifecycle state。
- `evidence_paths` - 支持 transition 的轻量路径或 command labels（命令标签）。
- `rollback_ref` - 需要恢复 pre-merge mainline（合并前主线）时使用的本地 backup ref。
- `local_main_commit` - 包含已集成 package 的 local `main` commit。
- `cleanup_decision` - 定义该 transition 的 cleanup 是 preserved（保留当前本地 worktree/branch 供后续处理）、deferred（延后到单独清理门禁）还是 executed（已通过受保护 helper 执行清理）。
- `reason` - exceptional 或 operator-driven transitions（操作者驱动转换）的可读解释。
- `remote_publication_authorized=false` - 明确标记 remote mutation（远端变更）仍然被阻止。

Integration/completion states（集成/完成状态）还会保留既有 checker 要求的 completion fields（完成字段）：

- `completed_at` - integration 或 cleanup completion evidence（完成证据）的 timestamp。
- `rollback_ref` - 需要恢复 pre-merge mainline 时使用的本地 backup ref。
- `local_main_commit` - 包含已集成 package 的 local `main` commit。
- `cleaned_worktree` - worktree cleanup result（工作树清理结果）的路径或状态。
- `deleted_branch` - local branch deletion evidence（本地分支删除证据）或 preservation status（保留状态）。
- `remote_sync_status` - state field means whether GitLab/GitHub publication is blocked（未获远端变更授权）、pending（已完成本地集成但仍需显式远端发布）还是 completed（已有远端发布或镜像同步证据）。

## Integration points

`tools/complete_local_flow_to_remote_gate.py` 在 local fast-forward merge（本地快进合并）和 post-merge local gate（合并后本地门禁）之后记录 `merged-local-main` transition。

`tools/cleanup_integrated_worktree.py` 在移除 worktree 并删除已合并本地 feature branch 后，记录或规范化 `cleaned` transition。primary root（主目录）下 preserved completed claim（已保留完成认领）携带 cleaned lifecycle evidence。

## Safety

helper 在缺少 rollback evidence 和 local-main evidence 时拒绝推进 integration states。Cleanup states（清理状态）要求 cleanup evidence。除非未来显式授权的 remote flow（远端流程）更新独立 remote evidence，否则 remote publication 保持关闭。
