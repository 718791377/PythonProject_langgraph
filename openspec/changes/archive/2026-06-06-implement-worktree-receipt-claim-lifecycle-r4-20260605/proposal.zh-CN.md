# 变更：实现 Worktree Receipt Claim Lifecycle R4

## Problem

仓库已经能校验 worktree task receipt（工作树任务收据）与 branch-matching claim（与分支匹配的会话认领）的 lifecycle label（生命周期标签），但实际运行时推进仍然是手动且分散的。`tools/complete_local_flow_to_remote_gate.py` 会记录本地 `main` 完成信息，`tools/cleanup_integrated_worktree.py` 会保留清理证据，但还没有一个共享 helper（辅助脚本）能用统一 transition ledger（状态转换账本）推进 `active`、`ready-to-merge`、`merged-local-main`、`completed`、`cleaned`、`paused`、`superseded` 或 `stale`。

## Goals

- 增加一个专用 lifecycle advancement helper（生命周期推进辅助脚本），用于同步更新 worktree receipt 和 branch-matching claim。
- 要求每次 transition（状态转换）记录 owner（记录者）、previous state（前一状态）、next state（下一状态）、timestamp（时间戳）、evidence paths（证据路径）、适用时的 rollback ref（回滚引用）以及 cleanup decision（清理决策）。
- 默认保持 remote publication unauthorized（远端发布未授权）。
- 让 local-main completion（本地 `main` 完成证据）和 safe cleanup flow（安全清理流程）共享同一套 transition evidence（转换证据）。
- 更新 implementation plan pair（实施方案双语文件）和 stable spec（稳定规格），让冷启动会话能识别 R4 行为。

## Scope

- `tools/advance_worktree_task_lifecycle.py` - 新增 lifecycle state transition（生命周期状态转换）辅助脚本。
- `tools/complete_local_flow_to_remote_gate.py` - 通过共享 transition helper 记录 local-main completion。
- `tools/cleanup_integrated_worktree.py` - 安全清理后规范化 `cleaned` lifecycle evidence。
- 覆盖正常 transition 和异常 transition 的测试。
- 为 multi-session worktree isolation（多会话工作树隔离）补充 OpenSpec delta（变更规格）。

## Non-goals

- 不变更 GitLab/GitHub。
- 不执行 remote publication（远端发布）或 mirror sync（镜像同步）。
- 不强制删除 branch、remote ref、backup ref 或未知 dirty work（未分类脏工作）。
- 不启动 durable team（持久团队）。

## Validation

- 聚焦 lifecycle helper 测试。
- 既有 worktree receipt、complete-flow、cleanup、ROB 和 local-flow 测试。
- 仓库 pre-commit update/archive review（提交前更新/归档审查）。
- OpenSpec guard 与 local CI gate。
