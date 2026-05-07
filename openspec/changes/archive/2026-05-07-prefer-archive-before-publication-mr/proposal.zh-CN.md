# 提案：默认采用发布前归档的单 MR 包

## Why

先发 implementation MR、之后再单独发 archive MR，会让 `main` 短暂留下 completed active changes，并额外消耗 GitLab pipeline 配额。仓库已经采用 local-first batching（本地优先批量发布）来节省 runner minutes，因此小型且本地验证通过的 OpenSpec change 应作为一个完整发布包发布。

## What Changes

让仓库发布流程默认在打开 GitLab MR 之前，先归档已经本地完成、验证通过、准备发布的小型 OpenSpec change。

默认发布包应在一个 GitLab MR 中同时包含实现或文档变更、已归档的 OpenSpec change，以及被提升后的 stable spec 更新。

## 范围

- 更新 `AGENTS.md` 的发布流程指导。
- 更新双语 multi-session worktree isolation governance policy（多会话工作区隔离治理策略）。
- 更新双语 OPSX project usage policy（OPSX 项目使用策略）。
- 增加 OpenSpec requirements（需求），区分 single-MR default（单 MR 默认流程）和 two-MR exceptions（双 MR 例外）。

## 非目标

- 不取消 GitLab-first review 和 pipeline 门禁。
- 不强迫大型或高风险实现工作在远端评审前归档。
- 不为了节省 runner 使用量而合并无关工作。
- 不在用户确认前发布分支。
