# Proposal: 增加本地不得落后远端规则

## 摘要

要求本地仓库基线在可写工作和远端发布前保持不落后于权威 GitLab 远端。

## 范围

- 更新仓库发布指令。
- 更新启动摘要。
- 更新 multi-session worktree isolation governance policy。
- 增加 OpenSpec requirement，用来约束工作和发布决策前的本地远端新鲜度。

## 非目标

- 不取消 local-first batching（本地优先批量发布）。
- 不要求每个本地 checkpoint 都推送远端。
- 不允许为了强制对齐而破坏性 reset 或清理脏工作。
