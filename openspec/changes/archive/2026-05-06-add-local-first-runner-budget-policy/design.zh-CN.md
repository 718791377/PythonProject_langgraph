# Design: 本地优先 runner 配额策略

## 策略形态

GitLab-first 仍然是权威远端集成路径。新规则改变的是远端发布时机，不改变权威顺序。

本地优先流程是：

1. 在 feature branch 和专用 worktree 上准备工作。
2. 在本地 commit 并验证。
3. 只有相关小变更共享同一个 review topic 和 rollback boundary（回退边界）时，才合并到一个 MR。
4. 只有本地验证通过后，才推送到 GitLab；除非用户要求提前跑远端 pipeline。
5. 只有 GitLab pipeline 成功后才合并。
6. 把 exact GitLab main commit 同步到 GitHub。

## 放置位置

该规则应放在：

- `AGENTS.md` - Codex 会话读取的仓库指令表面。
- `docs_bilingual/project_startup_summary.md` 和 `docs_bilingual/project_startup_summary.zh-CN.md` - 冷启动摘要。
- `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md` 和 `.zh-CN.md` - Git worktrees、branches、GitLab main 和 GitHub sync safety 的治理权威文件。

## 安全边界

该规则用于减少 runner 使用量，但不能隐藏 review 风险。无关主题仍然必须拆成独立 MR，因为回退安全和可评审性优先于节省 runner minutes。
