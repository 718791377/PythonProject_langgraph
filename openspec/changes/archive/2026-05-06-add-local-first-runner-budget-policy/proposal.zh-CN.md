# Proposal: 增加本地优先 runner 配额策略

## 摘要

记录 local-first batching（本地优先批量发布）策略，在保留 GitLab-first 发布权威的同时，减少不必要的 GitLab runner minutes 消耗。

## 范围

- 更新仓库启动指令，让新会话先看到本地优先批量发布规则。
- 更新 startup summaries，让冷启动会话尽早读取 runner 配额规则。
- 更新 multi-session worktree governance policy，使远端推送前的本地验证成为默认流程。
- 增加 OpenSpec delta requirement，用于约束本地优先 MR 批量发布和提前跑远端 pipeline 的例外。

## 非目标

- 不取消 GitLab-first review 和 merge 权威。
- 不移除 GitLab pipelines 或 CI gates。
- 不改变 GitHub 作为合并后镜像的行为。
- 本次 docs-only change 不新增 runtime scripts。
