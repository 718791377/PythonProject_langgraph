# Proposal: 增加发布时机建议规则

## 摘要

要求当前会话模型在推送 GitLab 之前，先判断本地批次是否适合远端发布，并向用户建议 publish（发布）或 wait（继续等待）。

## 范围

- 更新仓库发布指令。
- 更新启动摘要。
- 更新 multi-session worktree isolation governance policy。
- 增加 stable OpenSpec requirement，用来约束模型提出发布时机建议。

## 非目标

- 不把模型变成最终发布权威。
- 不绕过 GitLab-first review、GitLab pipeline gates 或 GitHub post-merge mirroring。
- 本次 docs-only change 不新增 runtime scripts。
