# formalize-early-worktree-release-policy

## 为什么

已完成的 feature worktree 目前通常会一直保留到远端发布完全结束。这样虽然安全，但会让本地执行面开放得更久，也会增加多会话协同时的噪声。仓库需要一条更清晰的规则：把“释放已经本地验证干净的 feature worktree”和“删除仍承载发布状态的 feature branch”分开处理。

## 变更内容

- 明确记录：feature worktree 在本地验证通过，并且所有需要保留的文件已经提交、转移、摘要记录或明确丢弃之后，可以删除。
- 明确记录：本地和远端 feature branch 必须保留到 GitLab MR 已合并、本地 `main` 已快进、GitHub `main` 已同步之后。
- 明确记录文件分类清理规则，覆盖已跟踪文件、未跟踪文件、本地证据、缓存、OCR 输出、私有文件、版权文件和大文件。
- 扩展 worktree hygiene checker，让冷启动会话可以分别看到干净 feature worktree 的释放候选状态和 branch 清理就绪状态。

## 能力范围

- codex-repository-multi-session-worktree-isolation

## 影响范围

- 治理文档：`docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md`，英文 worktree 隔离策略。
- 治理文档：`docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md`，中文对照策略。
- 检查脚本：`tools/check_worktree_session_hygiene.py`，只读 Git worktree hygiene checker。
- 测试：`test/check_worktree_session_hygiene.test.py`，worktree hygiene checker 的单元测试。